#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import logging
import os
import pytz
from django.http.response import HttpResponse
from datetime import datetime

from .. import config
from ..models import TextStats


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


upload_location = config.UPLOAD_LOCATION


def eval_str(s):
    if isinstance(s, str):
        try:
            return json.loads(s)
        except:
            pass
    return s


def get_text_names():
    return list(set([
      text.filename for text in TextStats.objects.all()
    ]))


def delete_old_texts():
    max_live_time = config.MAX_LIVE_TIME
    now = datetime.now()
    utc = pytz.UTC
    for text in TextStats.objects.all():
        if utc.localize(now) > (text.date_added + max_live_time):
            text.delete()
            if text.filename in get_text_names():
                try:
                    os.remove(os.path.join(config.OUTPUT_DIR, text.filename))
                except:
                    pass

def automatic_delete(request):
    time_step = config.CLEANUP_TIME_STEP
    # print(
    #   'The database will be clean up every %s seconds.' % (time_step.total_seconds()),
    #   'The texts stored in the database longer than %s days are to be deleted.' % (config.MAX_LIVE_TIME.days),
    #   'The annotated text is to be deleted if there is no live text instance with the same name exists.'
    #   )
    delete_old_texts()
    return HttpResponse("""
      The database will be clean up every %s seconds.
      The texts stored in the database longer than %s days are to be deleted.
      The annotated text is to be deleted if there is no live text instance with the same name exists.
      """% (time_step.total_seconds(), config.MAX_LIVE_TIME.days))

def visualise_text(text):
    """
    return metadata, sentences, paragraphs for a selected text
    """
    data = {
      'text_name': text.filename,
      'metadata': False,
      'sentences': [],
      'paragraphs': [],
      'message': ''
    }

    if eval_str(text.labels):
      data['metadata'] = {}
      data['metadata']['label'] = list(eval_str(text.labels).keys())
      data['metadata']['data'] = eval_str(text.labels)
    for sent in text.sentences:
        sent_dict = sent.__dict__.copy()
        sent_dict['tokens'] = [{**token.__dict__, 'highlight':None} for token in sent.tokens]
        data['sentences'].append(sent_dict)
    
    data['paragraphs'] = [str(p) for p in text.paragraphs]
    return data

from django.utils.encoding import smart_str

def handle_uploaded_file(f):
    fname = str(f)
    dest = upload_location + fname
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def str_to_bool(s):
    return True if s.lower() == "true" else False

# Remove any empty lines in the beginning
def rm_blanks(text_list):
    while text_list:
        if text_list[0].strip() == '':
            del text_list[0]
        else:
            text_list[0] = text_list[0].lstrip()
            break
    return text_list


def checkbox_to_bool(s):
    return True if s == "on" else False


def get_md5(file):
    import hashlib
    try:
        mystr = '<' + ' '.join(file.metadata_labels) + '>\n'

        for text in file.texts:
            mystr += '<' + ' '.join(text.metadata) + '>'
            mystr += '\n'
            for sentence in text.sentences:
                for token in sentence.tokens:
                    mystr += \
                    token.text_id + '\t' +\
                    token.token_id + '\t' +\
                    token.form + '\t' +\
                    token.norm + '\t' +\
                    token.lemma + '\t' +\
                    token.upos + '\t' +\
                    token.xpos + '\t' +\
                    token.feats + '\t' +\
                    token.ufeats + '\t' +\
                    token.head + '\t' +\
                    token.deprel + '\t' +\
                    token.deps + '\t' +\
                    token.misc
                mystr += '\n'
        hash_md5 = hashlib.md5()
        hash_md5.update(mystr)
    except:
        return None
    return hash_md5.hexdigest()
   
