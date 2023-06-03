"""
module to facilitate text downloading
"""
import csv
import codecs
import json
import logging
import os
import re
from datetime import datetime

import pandas as pd

from swegram_main.config import (
    COLUMN_DELIMITER,
    METADATA_DELIMITER_LEBAL, METADATA_DELIMITER_LEBAL, METADATA_DELIMITER_TAG,
    METADATA_FINAL, METADATA_INITIAL,
    OUT_FILE, OUTPUT_DIR, OUT_STATS_FILE 
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SWEDISH_CONLLU_HEADER = [
    'Paragraph.sentence_id', 'token_id', 'form', 'norm', 'lemma', 
    'upos', 'xpos', 'feats', 'ufeats', 'head', 'deprel', 'deps', 'misc'
]
ENGLISH_CONLLU_HEADER = [tag for tag in SWEDISH_CONLLU_HEADER if tag != 'ufeats']


def _generate_txt_file_header(lang, time_stamp):
    """generate file header"""
    return "# Swegram \n" \
           f"# Time: {time_stamp}\n" \
           f"# Language: {lang}"


def _convert_level_name(level):
    """convert into full name for the linguistic level"""
    if level == 'para':
        return 'paragraph'
    if level == 'sent':
        return 'sentence'
    return level


def _generate_stats_txt_file_header(
    texts, overview_detail, levels,
    output_form, time_stamp, lang
):
    return "Swegram Statistics\n" \
           f"Language: {lang}\n" \
           f"Time: {time_stamp}\n" \
           f"Ouput form: {output_form}\n" \
           f"Selected texts: {','.join([text.filename.rsplit('.', maxsplit=1) for text in texts])}\n" \
           f"Overview/Detail: {','.join(overview_detail)}\n" \
           f"Linguistic levels: {','.join([_convert_level_name(level) for level in levels])}\n" \
           f"\n"


def _generate_stats_txt_block_header(is_overview, level):
    return f"OverviewDetail: {is_overview}\n" \
           f"Linguistic level: {_convert_level_name(level)}\n\n"


def _generate_txt_text_header(text, index):
    """generate text header"""
    comments = f"\n\n# Name: {text.filename}\n" \
               f"# Size: {text.file_size}\n" \
               "# Tokenized: True\n" \
               f"# Normalized: {text.normalized}\n" \
               f"# PoS tagged: {text.parsed}\n\n"
    if index > 0 and not text.has_labels:
        return '<>\n' + comments.lstrip()
    return comments


def _generate_csv_file_header(lang, time_stamp, writer):
    """generate header for csv file"""
    writer.writerow(["# Swegram"])
    writer.writerow(["# Time:", time_stamp])
    writer.writerow(["# Language:", lang])


def _generate_csv_text_header(text, index, writer):
    """generate csv text header"""
    if index > 0 and not text.has_labels:
        writer.writerow(["<>"])
    writer.writerow(["# Name:", text.filename])
    writer.writerow(["# Size:", text.file_size])
    writer.writerow(["# Tokenized:", "True"])
    writer.writerow(["# Normalized:", text.normalized])
    writer.writerow(["# PoS tagged:", text.parsed])


def _generate_xlsx_file_header(lang, time_stamp, writer):
    """generate header for xlsx file"""
    date, time = time_stamp.split(maxsplit=1)
    info = pd.DataFrame([
            [date], [time], [lang]
        ],
        index=['Date', 'Time', 'Language'],
        columns=['Swegram']
    )
    info.to_excel(writer, sheet_name="Basic information for annotated texts")


def _generate_xlsx_text_header(text, writer):
    """generate xlsx text header"""
    comments = pd.DataFrame([
            [text.filename], [text.file_size], [True],
            [text.normalized], [text.parsed],
            [''] if text.has_label is False else [_parse_labels(text.labels)]
        ],
        index=['Name', 'Size', 'Tokenized', 'Normalized', 'PoS tagged', 'Metadata']
    )
    comments.to_excel(writer, header=False, sheet_name=f"Setting {text.filename.rsplit('.', maxsplit=1)[0]}")


def _generate_txt(out_file, text_list, lang, time_stamp):
    """generate texts with plain text"""
    out_file.write(_generate_txt_file_header(lang, time_stamp))
    for index, text in enumerate(text_list):
        out_file.write(_generate_txt_text_header(text, index))
        with codecs.open(os.path.join(OUTPUT_DIR, text.filename), 'r', encoding='utf-8') as text:
            out_file.write(text.read())


def _generate_stats_txt_body(temp_file, lang, texts, is_overview, level, selected_features):
    """generate statistics in form of text"""
    temp_file.write(_generate_stats_txt_block_header(is_overview, level))
    if is_overview.lower() == 'overview':
        ...
        

def _generate_csv(out_file, text_list, lang, time_stamp):
    """generate texts in form of csv"""
    csv_writer = csv.writer(out_file, delimiter=COLUMN_DELIMITER, escapechar="\\", quoting=csv.QUOTE_NONE)
    _generate_csv_file_header(lang, time_stamp, csv_writer)
    for index, text in enumerate(text_list):
        _generate_csv_text_header(text, index, csv_writer)
        for line in codecs.open(os.path.join(OUTPUT_DIR, text.filename)).readlines():
            if line.strip():
                csv_writer.writerow(line.strip().split('\t'))


def _generate_xlsx_text_body(text, lang, writer):
    """writing the text into excel file"""
    texts = []
    if lang == 'en':
        columns, length = ENGLISH_CONLLU_HEADER, 12
    elif lang == 'sv':
        columns, length = SWEDISH_CONLLU_HEADER, 13
    else:
        raise Exception(f"Language code {lang} is not supprted. Valid language codes: sv, en")
    with codecs.open(os.path.join(OUTPUT_DIR, text.filename), mode='r', encoding='utf-8') as input_file:
        line = input_file.readline()
        while line:
            if re.fullmatch(r'^%s.+%s$' % (METADATA_INITIAL, METADATA_FINAL), line.strip()):
                continue
            if line.startswith('#'):
                continue
            if line.strip():
                tabs = line.split('\t')
                if len(tabs) < length:
                    tabs.extend(['_' for _ in range(length-len(tabs))])
                texts.append(tabs)
            line = input_file.readline()
        content = pd.DataFrame(texts, columns=columns)
        content.to_excel(writer, index=False, sheet_name=text.filename.rsplit('.', maxsplit=1)[0])


def _generate_xlsx(out_file, text_list, lang, time_stamp):
    """generate texts in form of csv"""
    with pd.ExcelWriter(path=out_file.name, engine='openpyxl') as writer:
        _generate_xlsx_file_header(lang, time_stamp, writer)
        for text in text_list:
            _generate_xlsx_text_header(text, writer)
            _generate_xlsx_text_body(text, lang, writer)


def _parse_labels(text):
    """parse labels"""
    labels = json.loads(text.labels)
    return METADATA_DELIMITER_LEBAL.join([
        f"{key}{METADATA_DELIMITER_TAG}{value}"
        for key, value in labels.items()
    ])


def download_helper(text_list, lang, format, temp_file):
    """main function to download the files"""
    now = datetime.now().strftime('%Y-%m-%d %H%M')
    if format == '.txt':
        _generate_txt(temp_file, text_list, lang, now)
    elif format == '.csv':
        _generate_csv(temp_file, text_list, lang, now)
    elif format == '.xlsx':
        _generate_xlsx(temp_file, text_list, lang, now)
    else:
        logger.error(f"Unsupported format for downloading: {format}")


def _generate_stats_txt():
    """generate statistics for text"""
    ...


def _generate_stats_csv():
    """generate statistics for csv"""
    ...

def _generate_stats_xlsx():
    """generate statistics for xlsx"""
    ...



def download_stats_helper(
    text_list, lang, format, temp_file,
    overview_detail, levels, selected_features, feature_list
):
    """
    main function to download the statistics
    These factors are considered when downloading statistics:
    1. text selection
    2. lang
    3. overview or|and detail
    4. levels: text, paragraph, sentence
    5. selected features
    """
    now = datetime.now().strftime('%Y-%m-%d %H%M')
    if format == '.txt':
        _generate_stats_txt(temp_file, text_list, lang, now)
    elif format == '.csv':
        _generate_stats_csv(temp_file, text_list, lang, now)
    elif format == '.xlsx':
        _generate_stats_xlsx(temp_file, text_list, lang, now)
    else:
        logger.error(f"Unsupported format for downloading statistics: {format}")

