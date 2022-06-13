# This script is to download either the annotated text (selected) or the statisticss

# target of annotated texts
# 1. make sure which texts are selected
#   options: all texts, selected texts, text
# 2. check if the text is normalized
# 3. check if the text has the metadata
# 

# target of downloading statistics
# 1. make sure which text(s) are selected
# 2. make sure which level is to be selected
# 3. make sure which features are going to be downloaded
# 4. make sure if the average values are included

# Create | Merge files 
# Download 


"""
text_list:
    filename
    file_id
    file_size
    date_added
    eligible
    activated
    id
    normalized
    has_label
    labels
"""
from datetime import datetime
import codecs
import csv
import json
import os
import re

from django.http import FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import pandas as pd

from ..config import METADATA_DELIMITER_LEBAL, METADATA_DELIMITER_TAG, METADATA_FINAL, METADATA_INITIAL 
from ..config import OUTPUT_DIR, OUT_FILE, OUT_STATS_FILE, COLUMN_DELIMITER
from .features import get_overview_features, get_detail_features
from .helpers import eval_str
from .statistics import get_text_list

def get_text_comments(text, index):
    comments = """\n\n# Name: %s\n# Size: %s\n# Tokenized: %s\n# Normalized: %s\n# PoS tagged: %s\n\n""" % \
              (text.filename, text.file_size, True, text.normalized, text.parsed)
    if index > 0 and not text.has_label:
        return '<>\n' + comments.lstrip() # add text delimiter when the text does not contain metadata
    return comments

def get_file_commments(lang, now):
    return """# Swegram \n# Time: %s \n# Language: %s""" % (now, lang)

@ensure_csrf_cookie
def download_texts(request):
    body = json.loads(request.body)
    text_list = get_text_list(request)
    output_format = body['outputForm']
    lang = body['lang']
    return download_text_file(text_list, lang, output_format)
    
def create_file_for_text_txt(text_list, lang, out_file_name, now):
    with codecs.open(out_file_name, mode='w', encoding='utf-8') as out_f:
        out_f.write(get_file_commments(lang, now))
        for index, text in enumerate(text_list):
            out_f.write(get_text_comments(text, index))
            with codecs.open(os.path.join(OUTPUT_DIR, text.filename), mode='r', encoding='utf-8') as f:
                out_f.writelines(f.readlines())
          

def remove_extention(filename):
    return '.'.join(filename.split('.')[:-1])

def _csv_comment_format(line, text_writer):
    line_elements = line.split(':')
    head = line_elements[0].lstrip().strip()
    tail = ' '.join(line_elements[1:]).lstrip().strip()
    if tail:
        text_writer.writerow([head+':', tail])
    else:
        text_writer.writerow([head])
    return text_writer

def create_file_for_text_csv(text_list, lang, out_file_name, now):
    with codecs.open(out_file_name, mode='w', encoding='utf-8', newline='') as csvfile:
        text_writer = csv.writer(
          csvfile, 
          delimiter=COLUMN_DELIMITER, 
          escapechar="\\",
          quoting=csv.QUOTE_NONE)
        for line in get_file_commments(lang, now).split('\n'):
            text_writer = _csv_comment_format(line, text_writer)
        for index, text in enumerate(text_list):
            text_comments = get_text_comments(text,index)
            for comment in text_comments.split('\n'):
                if comment.strip():
                    text_writer = _csv_comment_format(comment, text_writer)
            with codecs.open(os.path.join(OUTPUT_DIR, text.filename), mode='r', encoding='utf-8') as f:
                for text_line in f.readlines():
                    if text_line.strip():
                        text_writer.writerow(text_line.strip().split('\t'))

def create_file_for_text_xlsx(text_list, lang, out_file_name, now): 
    with pd.ExcelWriter(out_file_name) as writer:
        date, time = now.split()
        text_info = pd.DataFrame([
            [date],
            [time],
            [lang]
          ], 
          index=['Date', 'Time', 'Language'], 
          columns=['Swegram']
        )
        text_info.to_excel(writer, sheet_name="Basic information for annotated texts")

        for text in text_list:

            text_comment = pd.DataFrame([
                [text.filename],
                [text.file_size],
                [True],
                [text.normalized],
                [text.parsed],
                [''] if text.has_label is False else ['%s'.join([
                  '%s%s%s' % (label, METADATA_DELIMITER_TAG, value) for label, value in eval_str(text.labels).items()
                  ]) % tuple([METADATA_DELIMITER_LEBAL for _ in range(len(eval_str(text.labels))-1)])],
              ],
              index=['Name', 'Size', 'Tokenized', 'Normalized', 'PoS tagged', 'Metadata'],
            )
            text_comment.to_excel(writer, header=False, sheet_name='Setting ' + remove_extention(text.filename))
            with codecs.open(os.path.join(OUTPUT_DIR, text.filename), mode='r', encoding='UTF-8-sig') as f:
                # specify encoding to remove byte-order mark BOM from the beginning of the file
                text_lines = f.readlines()
            texts = []
            if lang == 'sv':
                columns = ['Paragraph.sentence_id', 'token_id', 'form', 'norm', 'lemma', 'upos', 'xpos', \
                          'feats', 'ufeats', 'head', 'deprel', 'deps', 'misc']
                column_num = 13
            elif lang == 'en':
                columns = ['Paragraph.sentence_id', 'token_id', 'form', 'norm', 'lemma', 'upos', 'xpos', \
                          'feats', 'head', 'deprel', 'deps', 'misc']
                column_num = 12
            for line in text_lines:
                if not line.strip(): # skip the empty line
                    continue
                if re.fullmatch(r'^%s.+%s$' % (METADATA_INITIAL, METADATA_FINAL), line.lstrip().strip()): # skip the line with metadata
                    continue
                if line[0] == '#':
                    continue
                tabs = line.split('\t')
                if len(tabs) < column_num:
                    tabs.extend(['_' for _ in range(column_num - len(tabs))])
                texts.append(tabs)
            content = pd.DataFrame(texts, columns=columns)
            content.to_excel(writer, index=False, sheet_name=remove_extention(text.filename))
                
def get_out_file_name(file_path, file_name, time_stamp, output_format):
    return ''.join([
      os.path.join(file_path, file_name),
      '-',
      time_stamp,
      output_format
    ])
    
def download_text_file(text_list, lang, output_format):
    now = datetime.now().strftime('%Y-%m-%d %H%M')
    
    out_file_name = get_out_file_name(OUTPUT_DIR, OUT_FILE, now, output_format)
    if output_format == '.txt':
        create_file_for_text_txt(text_list, lang, out_file_name, now)
    elif output_format == '.csv':
        create_file_for_text_csv(text_list, lang, out_file_name, now)
    elif output_format == '.xlsx':
        create_file_for_text_xlsx(text_list, lang, out_file_name, now)
    response = FileResponse(codecs.open(out_file_name, 'rb'), as_attachment=True)
    os.remove(out_file_name)
    return response

def get_full_level_name(level):
    if level == 'para':
        return 'paragraph'
    elif level == 'sent':
        return 'sentence'
    else:
        return level

def get_stats_comments(texts, overview_and_detail, levels, output_form, time, lang):
    title = "Swegram Statistics"
    selected_texts = "Selected texts: " + ",".join([remove_extention(text.filename) for text in texts])
    contain_overview_or_detail = "Overview/Detail: " + ", ".join(overview_and_detail)
    linguistic_levels = "Linguistic levels: " + ", ".join([get_full_level_name(level) for level in levels])
    return '\n'.join([
      title,
      'Language: ' + lang,
      'Time: ' + time,
      'Output form: ' + output_form,
      selected_texts,
      contain_overview_or_detail,
      linguistic_levels,
      '\n'
    ])

def get_stats_block_comments(isOverview, level):
    return '\n'.join([
      'Overview/Detail: %s' % isOverview,
      'Linguistic level: %s' % get_full_level_name(level),
      '\n'
    ])

def create_file_for_stats(out_file_name, texts, overview_and_detail, levels, output_form, time, lang):
    # create a file
    stats_comments = get_stats_comments(texts, overview_and_detail, levels, output_form, time, lang)
    with codecs.open(out_file_name, mode='w', encoding='utf-8') as f:
        f.write(stats_comments)

def features2csv(features, csv_writer):
    def feature_writer(feature): 
        csv_writer.writerow([
          feature['name'],
          feature.get('scalar', '-'),
          feature.get('mean', '-'),
          feature.get('median', '-')
        ])
    csv_writer.writerow('Name Scalar Mean Median'.split())
    for aspect in features['data']:
        if aspect['aspect'] == 'morph':
            initialized_morph = False
            for children in aspect['data']:
                for child in children['children']:
                    if initialized_morph is False:
                        title=['Linguistic aspect:', aspect['aspect']]
                        csv_writer.writerow(title)
                        initialized_morph = True
                    feature_writer(child)
        else:
            if aspect['data']:
                title=['Linguistic aspect:', aspect['aspect']]
                csv_writer.writerow(title)
            for feature in aspect['data']:
                feature_writer(feature)
    return csv_writer

def features2xlsx(features):
    scalar_list, row_name_list = [], []
    row_name_list = []
    def feature_writer(feature):
        scalar_list.append([
          feature.get('scalar', '-'),
          feature.get('mean', '-'),
          feature.get('median', '-')
        ])
        row_name_list.append(feature.get('name'))
    for aspect in features['data']:
        if aspect['aspect'] == 'morph':
            initialized_morph = False
            for children in aspect['data']:
                for child in children['children']:
                    if initialized_morph is False:
                        scalar_list.append([aspect['aspect'], '', ''])
                        row_name_list.append('Linguistic aspect:')
                        initialized_morph = True
                    feature_writer(child)
        else:
            if aspect['data']:
                scalar_list.append([aspect['aspect'], '', ''])
                row_name_list.append('Linguistic aspect:')
            for feature in aspect['data']:
                feature_writer(feature)
    return # pd.DataFrame(scalar_list, index=row_name_list, columns=['Scalar', 'Mean', 'Median'])


def features2file(feature_dict, filename):
    """
    features: {'data': [], 'content': '', 'text':  }
    """
    def feature_writer(feature, file):
        file.write('%s\t%s\t%s\t%s' % (feature['name'], feature.get('scalar', '-'), feature.get('mean', '-'), feature.get('median', '-')))
        file.write('\n')
    with codecs.open(filename, mode='a+', encoding='utf-8') as f:
        if 'content' in feature_dict:
            f.write('Content: %s' % feature_dict['content'])
            f.write('\n')
        f.write('\tName\tScalar\tMean\tMedian\n')
        for aspect in feature_dict['data']:
            if aspect['aspect'] == 'morph':
                initialized_morph = False
                for children in aspect['data']:
                    for child in children['children']:
                        if initialized_morph is False:
                            f.write('Linguistic aspect: %s' % aspect['aspect'])
                            f.write('\n')
                            initialized_morph = True
                        feature_writer(child, f)
            else:
                if aspect['data']:
                    f.write('Linguistic aspect: %s' % aspect['aspect'])
                    f.write('\n')
                for feature in aspect['data']:
                    feature_writer(feature, f)
            f.write('\n')
            

def write_features2file(features, filename, detail=False):
    with codecs.open(filename, mode='a+', encoding='utf-8') as f:
        if detail:
            for feature_dict in features:
                features2file(feature_dict, filename)
        else:
            features2file(features, filename)


def write_stats_for_created_file(out_file_name, lang, texts, isOverview, level, removed_features):
    with codecs.open(out_file_name, mode='a+', encoding='utf-8') as f:
        f.write('\n\n')
        block_comments = get_stats_block_comments(isOverview, level)
        f.write(block_comments)
        f.write('\n')
    if isOverview.lower() == 'overview':
        features = get_overview_features(texts, lang, level, removed_features)
        write_features2file(features, out_file_name)
    elif isOverview.lower() == 'detail':
        features = get_detail_features(texts, lang, level, removed_features)
        write_features2file(features, out_file_name, detail=True)

def get_removed_features(options, chosen_features):
    leaf_dict = get_leaf_dict(options)
    chosen_feature_values = [f[-1] for f in chosen_features]
    for feature in chosen_feature_values:
        del leaf_dict[feature]
    return list(leaf_dict.values())

def get_leaf_dict(options, leaf_dict={}):
    
    for block in options:
        if 'children' in block:
            leaf_dict = get_leaf_dict(block['children'], leaf_dict)
        else:
            leaf_dict[block['value']] = block['label']
    return leaf_dict

def download_stats_file(request, *args, **kwargs):
    """
    These factors are considered when downloading statistics
      1. text selection
        a. lang
      2. overview or|and detail
      3. levels: text, paragraph, sentence
      4. features: which features are involved
    """
    body = json.loads(request.body)
    overview_detail = body['overviewOrDetail']  # list
    levels = body['levels']                     # list
    chosen_features = body['chosenFeatures']    # list
    feature_list = body['featureList']
    output_format = body['outputForm']            # string
    lang = body['lang']
    removed_features = get_removed_features(feature_list, chosen_features)
    now = datetime.now().strftime('%Y-%m-%d %H%M')

    text_list = get_text_list(request)

    out_file_name = get_out_file_name(OUTPUT_DIR, OUT_STATS_FILE, now, output_format)
    if output_format == '.txt':
        create_file_for_stats(out_file_name, text_list, overview_detail, levels, output_format, now, lang)
        for isOverview in overview_detail:
            for level in levels:
                write_stats_for_created_file(out_file_name, lang, text_list, isOverview, level, removed_features)
    elif output_format == '.csv':
        with codecs.open(out_file_name, mode='w', encoding='utf-8', newline="") as csvfile:
            stats_writer = csv.writer(
              csvfile, 
              delimiter=";",
              escapechar="\\",
              quoting=csv.QUOTE_NONE)
          
            for line in get_stats_comments(text_list, overview_detail, levels, output_format, now, lang).split('\n'):
                if line.strip():
                    # line = line.replace(',', ' ')
                    try:
                        label, value = line.strip().split(':')
                        stats_writer.writerow([label+':', value.lstrip()])
                    except Exception:
                        stats_writer.writerow(line.strip().split(':'))
            
            for index, isOverview in enumerate(overview_detail, 1):
                for level_index, level in enumerate(levels, 1):
                    # for stats_comment in get_stats_block_comments(isOverview, level).split('\n'):
                    #     if stats_comment.strip():
                    #         stats_writer.writerow([str(index)+'.'+str(level_index)] + stats_comment.split(':'))
                    if isOverview == 'overview':
                        stats_writer.writerow([
                          '%d.%d' % (index, level_index),
                          '%s-%s' % (isOverview, get_full_level_name(level)) 
                        ])
                        features = get_overview_features(text_list, lang, level, removed_features)
                        stats_writer = features2csv(features, stats_writer)
                    elif isOverview == 'detail':
                        features_list = get_detail_features(text_list, lang, level, removed_features) 
                        for block_index, features in enumerate(features_list, 1):
                            stats_writer.writerow([
                              '%d.%d.%d' % (index, level_index, block_index),
                              '%s-%s' % (isOverview, get_full_level_name(level))
                            ])
                            stats_writer = features2csv(features, stats_writer)
    elif output_format == '.xlsx':
        pass
        with pd.ExcelWriter(out_file_name) as writer:
            date, time = now.split()
            text_info = pd.DataFrame([
              [lang],
              [date],
              [time],
              [output_format],
              [','.join([remove_extention(text.filename) for text in text_list])],
              [','.join(overview_detail)],
              [','.join(levels)]
            ],
            index=['Language', 'Date', 'Time', 'Output form', 'Selected texts', 'Overview/Detail', 'Levels'],
            columns=["Swegram Statistics"]
            )
            text_info.to_excel(writer, sheet_name="Basic information for statistics")

            for index, isOverview in enumerate(overview_detail, 1):
                for level_index, level in enumerate(levels, 1):
                    if isOverview == 'overview':
                        features = get_overview_features(text_list, lang, level, removed_features)
                        feature_data_set = features2xlsx(features)
                        feature_data_set.to_excel(writer, sheet_name="%d.%d-%s-%s" % (index, level_index, isOverview, level))
                    elif isOverview == 'detail':
                        features_list = get_detail_features(text_list, lang, level, removed_features)
                        pd_data_list = []
                        for set_index, features in enumerate(features_list, 1):
                            pd_data_list.append(pd.DataFrame([[set_index, '','']], index=['block'], columns=['Scalar', 'Mean', 'Median']))
                            pd_data_list.append(features2xlsx(features))
                        feature_data_set = pd.concat(pd_data_list)
                        feature_data_set.to_excel(writer, sheet_name="%d.%d-%s-%s" % (index, level_index, isOverview, level))
    response = FileResponse(codecs.open(out_file_name, 'rb'), as_attachment=True)
    os.remove(out_file_name)
    return response
