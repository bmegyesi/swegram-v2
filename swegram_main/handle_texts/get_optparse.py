#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from .helpers import str_to_bool

def parse_post(request):
    dict = {"checkTokenize": 'False', "checkNormalization": 'False',\
    "checkPOS": 'False', "checkParse": 'False', "instant_analysis": 'False'}
    for entry in request.POST:
        if entry != "csrfmiddlewaretoken":
            dict[entry] = request.POST[entry].replace("on", "true")
    return dict

def select_columns(dict):
    columns = ""
    if 'col1' in dict: columns += "1,"
    if 'col2' in dict: columns += "2,"
    if 'col3' in dict: columns += "3,"
    if 'col4' in dict: columns += "4,"
    if 'col5' in dict: columns += "5,"
    if 'col6' in dict: columns += "6,"
    if 'col7' in dict: columns += "7,"
    if 'col8' in dict: columns += "8,"
    if 'col9' in dict: columns += "9,"
    if 'col10' in dict: columns += "10,"
    if 'col11' in dict: columns += "11,"
    if 'col12' in dict: columns += "12,"
    if 'col13' in dict: columns += "13,"
    return columns.rstrip(",")

def get_optparse(request, filename, tmp_dir, custom_filename=False):

    dict = parse_post(request)
    options = OptionParser
    options.columns = select_columns(dict)

    options.tmp_dir = tmp_dir

    options.tokenize = str_to_bool(dict['checkTokenize'])
    options.tag = str_to_bool(dict['checkPOS'])
    options.normalize = str_to_bool(dict['checkNormalization'])

    options.parse = str_to_bool(dict['checkPOS'])

    options.tagger = str(dict['tagger'])
    options.parser = str(dict['parser'])
    options.tokenizer = str(dict['tokenizer'])
    options.spellchecker = str(dict['spellchecker'])

    options.parser_model = str(dict['parser_model'])
    options.tagger_model = str(dict['tagger_model'])

    if not dict.get('compounds_method'):
        options.compounds_method = 'none'
    else:
        options.compounds_method = str(dict['compounds_method'])

    options.preserve_paragraphs = True
    options.preserve_metadata = True
    options.metadata_format = "<.*>"

    options.custom_filename = custom_filename

    options.instant_analysis = str_to_bool(dict['instant_analysis'])

    options.open = filename

    return options
