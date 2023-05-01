#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import T
import tempfile
import codecs

from datetime import datetime
import json
import shutil

import os
from django.core import serializers
import pandas as pd
import csv
import subprocess

from .pipeline import pipeline, pipeline_en

from ..handle_texts.pipeline.scripts.process import file2texts

from .get_optparse import get_optparse
from .helpers import handle_uploaded_file, checkbox_to_bool, eval_str
from .. import config
from .import_text import import_text, import_annotated_text

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from ..models import TextStats, Text, Paragraph, Sentence, Token

pipe_path       = config.PIPE_PATH
upload_location = config.UPLOAD_LOCATION

"""
note: we split the file into smaller ones if there are multiple labels.
      each meta line indicates that there is a following text.
"""

def labels2line(label_dict):
    return ''.join([
      config.METADATA_INITIAL,
      config.METADATA_DELIMITER_LEBAL.join([config.METADATA_DELIMITER_TAG.join([key, value]) for key, value in label_dict.items()]),
      config.METADATA_FINAL,
      '\n\n'
      ])

def update_rawlists_indent(raw_list):
    updated_list = []
    index = None
    for line in raw_list:
        if line.strip():
            line_index = line.split('\t')[0]
            if index is None:
                index = line_index
                updated_list.extend([line.strip()])
            elif index == line_index:
                updated_list.extend(['\n', line.strip()])
            else:
                if line_index.split('.')[0] == index.split('.')[0]:
                    updated_list.extend(['\n\n', line.strip()])
                else:
                    updated_list.extend(['\n\n\n', line.strip()])
                index = line_index
    return updated_list

def write_text2db(t): #input text instance
    ts = TextStats.objects.create(
      text_id    = t.id,
      lang       = t.lang,
      filename   = t.filename,
      file_size  = t.file_size,
      normalized = t.normalized,
      parsed     = t.parsed,
      has_label  = t.has_label,
      labels     = json.dumps(t.labels),
      number_of_paragraphs = len(t.paragraphs),
      number_of_sentences  = len(t.sentences) 
    )

    text = Text.objects.create(
      stats            = ts,
      general          = json.dumps(t.general),
      readability      = json.dumps(t.readability),
      morph            = json.dumps(t.morph)               if t.parsed else None,
      morph_average    = json.dumps(t.morph_average)       if t.parsed else None,
      lexical          = json.dumps(t.lexical)             if t.parsed else None,
      lexical_average  = json.dumps(t.lexical_average)     if t.parsed else None,
      syntactic        = json.dumps(t.syntactic)           if t.parsed else None,
      syntactic_average= json.dumps(t.syntactic_average)   if t.parsed else None,
      content          = '\n'.join([str(p) for p in t.paragraphs])
    )
    
    for paragraph in t.paragraphs:
        p = Paragraph.objects.create(
          text              = text,
          general           = json.dumps(paragraph.general),
          readability       = json.dumps(paragraph.readability),
          morph             = json.dumps(paragraph.morph)              if t.parsed else None,
          morph_average     = json.dumps(paragraph.morph_average)      if t.parsed else None,
          lexical           = json.dumps(paragraph.lexical)            if t.parsed else None,
          lexical_average   = json.dumps(paragraph.lexical_average)    if t.parsed else None,
          syntactic         = json.dumps(paragraph.syntactic)          if t.parsed else None,
          syntactic_average = json.dumps(paragraph.syntactic_average)  if t.parsed else None,
          content           = str(paragraph)
        )
        for sentence in paragraph.sentences:
            s = Sentence.objects.create(
              text        = text,
              paragraph   = p,
              text_index  = sentence.text_id,
              types       = json.dumps(sentence.types),
              ud_tree     = True if sentence.syntactic else False,
              general     = json.dumps(sentence.general),
              readability = json.dumps(sentence.readability),
              morph       = json.dumps(sentence.morph)      if t.parsed else None,
              lexical     = json.dumps(sentence.lexical)    if t.parsed else None,
              syntactic   = json.dumps(sentence.syntactic)  if t.parsed else None,
              content     = str(sentence)
            )
            for token in sentence.tokens:
                tok = Token.objects.create(
                  sentence = s,
                  compound_originals = token.compound_originals,
                  normalized         = token.normalized,
                  token_index        = token.token_id,
                  text_index         = token.text_id,
                  form               = token.form,
                  norm               = token.norm,
                  lemma              = token.lemma,
                  upos               = token.upos,
                  xpos               = token.xpos,
                  feats              = token.feats,
                  ufeats             = token.ufeats if t.lang == 'sv' else '',
                  head               = token.head,
                  deprel             = token.deprel,
                  deps               = token.deps,
                  misc               = token.misc,
                  path               = vars(token).get('path', "_"),
                  length             = vars(token).get('length', "_"),
                  dep_length         = vars(token).get('dep_length', None),
                )
                tok.save()



# def set_session(request, texts): # t here refers to a list of texts from the same file
#     for text in texts:
#         # for key in [
#         #   'general', 
#         #   'readability', 
#         #   'morph', 
#         #   'morph_average', 
#         #   'lexical', 
#         #   'lexical_average', 
#         #   'syntactic', 
#         #   'syntactic_average'
#         # ]:
#           # try:
#           #     print(vars(text)[key]['average'])
#           # except Exception:
#           #     pass
#           # print()
#         # print('text', vars(text))
#         write_text2db(text)
    
#     text_stats_list = []
#     for text in texts:
#         try:
#             ts = TextStats.objects.get(text_id=text.id)
#             text_stats_list.append(ts)
#         except Exception:
#             pass
#     request.session['text_list'] = [
#       *request.session.get('text_list', []), 
#       *text_stats_list
#     ]

#     for text in texts:
#         request = add_text_metadata(request, text)
#     request.session.modified = True
#     return request


@csrf_exempt
#@ensure_csrf_cookie
def upload_annotated_file(request, lang, *args, **kwargs):
    handle_uploaded_file(request.FILES['file_to_analyze'])
    
    filename = str(request.FILES['file_to_analyze'])

    #checked = uploaded_file_checker(upload_location + filename, lang, True, normalized)
    #if checked is False:
    #    print('the text is not standard')
    #    return JsonResponse({'success':0})
    original_filename = filename
    if os.path.splitext(filename)[1] == '.csv':
        textfile = ''.join([os.path.splitext(filename)[0], '.txt'])
        with open(os.path.join(upload_location, textfile), 'w') as new_text_file:
            with open(os.path.join(upload_location, filename), newline='') as csvfile:
                text_reader = csv.reader(csvfile, delimiter=config.COLUMN_DELIMITER)
                for row in text_reader:
                    row_line = '\t'.join(row)+'\n'
                    # new_text_file.write('\t'.join(row))
                    # new_text_file.write('\n')
                    new_text_file.write(row_line)
                    if row_line.startswith('#'):
                        new_text_file.write('\n')
        os.remove(os.path.join(upload_location, filename))
        filename = ''.join([os.path.splitext(filename)[0], '.txt'])

    elif os.path.splitext(filename)[1] == '.xlsx':
        textfile = ''.join([os.path.splitext(filename)[0], '.txt'])
        with open(os.path.join(upload_location, textfile), 'w', encoding='utf-8-sig') as new_text_file:
            xl_file = pd.ExcelFile(os.path.join(upload_location, filename))
            sheet_names = xl_file.sheet_names[1:] # skip the first page
            for index, sheet_name in enumerate(sheet_names):
                """
                even index sheet contains text information
                odd index sheet contains text content
                """
                if index % 2 == 0:
                    metadata = xl_file.parse(sheet_name).to_string().split('\n')[-1].split()   #[-1]
                    if metadata == 'NaN':
                        new_text_file.write('%s%s' % (config.METADATA_INITIAL, config.METADATA_FINAL))
                    else:
                        new_text_file.write('%s%s%s' % (config.METADATA_INITIAL, config.METADATA_DELIMITER_LEBAL.join(metadata[2:]), config.METADATA_FINAL))
                    new_text_file.write('\n')
                else:
                    text_lines = xl_file.parse(sheet_name).to_string().split('\n')
                    first_line = True
                    for text_line in text_lines[1:]: # skip the header
                        line = '\t'.join(text_line.split()[1:]).strip('\\n') # skip row index
                        if first_line:
                            print('first line', line)
                            first_line = False
                        new_text_file.write(line)
                        new_text_file.write('\n')
        # os.remove(os.path.join(upload_location, filename))
        filename = ''.join([os.path.splitext(filename)[0], '.txt'])

    elif os.path.splitext(filename)[1] != ".txt":
        try:
            subprocess.call(['unoconv', '--format=txt', upload_location + filename])
            # stdout_file = open(upload_location + os.path.splitext(filename)[0] + ".txt2", "w")
            # subprocess.call(['iconv', '-f', 'iso-8859-1', '-t', 'utf-8', upload_location + os.path.splitext(filename)[0] + ".txt"], stdout=stdout_file)
            # shutil.move(upload_location + os.path.splitext(filename)[0] + ".txt2", upload_location + os.path.splitext(filename)[0] + ".txt")
            filename = os.path.splitext(filename)[0] + ".txt"
        finally:
            os.remove(upload_location + original_filename)
    filenames, labels = file2texts(upload_location + filename)
    texts = []
    error_msgs = []
    for filename, label in zip(filenames, labels):
        try:
            has_not_error, text = import_annotated_text(request, lang, filename, label)
            if has_not_error:
                texts.append(text)
            else:
                error_msgs.extend(text)
        finally:
            try:
                os.remove(filename)
            except:
                pass
    if error_msgs or texts == []:
        return JsonResponse({'success': 0, 'error_msg': error_msgs})
    # request = set_session(request, texts)
        

        
    for text in texts:
        raw_contents_list = text.raw_contents_list
        updated_list = update_rawlists_indent(raw_contents_list)
        if text.has_label:
            label_line = labels2line(eval_str(text.labels))
            updated_list.insert(0, label_line)
        with open(os.path.join(config.OUTPUT_DIR, text.filename), 'w') as f:
            f.writelines(updated_list)
    text_stats_list = set_texts(texts)

    return JsonResponse({
      'success': 1,
      'text_stats_list': text_stats_list,
      })

@csrf_exempt
#@ensure_csrf_cookie
def annotate_uploaded_file(request, lang, *args, **kwargs):
    tmp_dir = tempfile.mkdtemp() + "/" # Used for the pipeline
    use_paste = False
    pasted_text = None
    for key in request.POST:
        if key == 'use_paste':
            if checkbox_to_bool(request.POST[key]):
                use_paste = True
        elif key == 'pasted_text':
            pasted_text = request.POST[key]


    if use_paste:
        tf = tempfile.NamedTemporaryFile(delete=False)
        with codecs.open(tf.name, 'wb', encoding='utf-8') as f:
            f.write(pasted_text)
        # file_path = tf.name
        filename = 'paste ' + datetime.now().strftime("%H:%M:%S") + '.txt'
        shutil.move(tf.name, upload_location + filename)
        options = get_optparse(request, upload_location + filename, tmp_dir, custom_filename=filename)

    else:
        handle_uploaded_file(request.FILES['file_to_annotate'])
        filename = str(request.FILES['file_to_annotate'])
        original_filename = filename
        
        if os.path.splitext(filename)[1] != ".txt":
            try:
                subprocess.call(['unoconv', '--format=txt', upload_location + filename])
                # stdout_file = open(upload_location + os.path.splitext(filename)[0] + ".txt2", "w")
                # subprocess.call(['iconv', '-f', 'iso-8859-1', '-t', 'utf-8', upload_location + os.path.splitext(filename)[0] + ".txt"], stdout=stdout_file)
                # shutil.move(upload_location + os.path.splitext(filename)[0] + ".txt2", upload_location + os.path.splitext(filename)[0] + ".txt")
                filename = os.path.splitext(filename)[0] + ".txt"
            finally:
                os.remove(upload_location + original_filename)
        options = get_optparse(request, upload_location + filename, tmp_dir)

    # If the user has removed some column, the text can't be used for analysis
    filenames, labels = file2texts(options.open)
    texts = []
    try:
        for filename, label in zip(filenames, labels):
            options.open = filename
            if lang == 'en':
                annotated_file_path, text_eligible = pipeline_en.run(options)
            else:
                annotated_file_path, text_eligible = pipeline.run(options)
            try:
                text = import_text(request, lang, label, annotated_file_path, text_eligible)
                texts.append(text)
                if label:
                    insert_label(annotated_file_path, label)
            finally:
                try:
                    os.remove(options.open)
                except:
                    pass
            
    finally:
        shutil.rmtree(tmp_dir)

    if not texts:
        return JsonResponse({'success': 0})
    
    text_stats_list = set_texts(texts)
    
    return JsonResponse({
      'success': 1,
      'text_stats_list': text_stats_list,
    })

def set_texts(texts):
    "write texts into database and write text stats into json, which is to be imported to localStorage"
    text_ids = []
    for text in texts:
        write_text2db(text)
        text_ids.append(text.id)
    text_stats_list = json.loads(serializers.serialize('json', TextStats.objects.filter(text_id__in=text_ids)))
    for text in text_stats_list:
        text['fields']['labels'] = json.loads(text['fields']['labels'])
    return text_stats_list

def insert_label(path, label):
    lines = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        line = f.readline()
        while line:
            lines.append(line)
            line = f.readline()
    meta = config.METADATA_DELIMITER_LEBAL.join([config.METADATA_DELIMITER_TAG.join([tag, value]) for tag, value in label.items()])
    meta = ''.join([config.METADATA_INITIAL, meta, config.METADATA_FINAL])
    lines.insert(0, meta+'\n\n')
    with open(path, 'w', encoding='utf-8-sig') as f:
        for line in lines:
            f.write(line)
