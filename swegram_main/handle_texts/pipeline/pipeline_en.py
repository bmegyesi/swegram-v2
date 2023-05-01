#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from optparse import OptionParser
import shutil
from .scripts.process import remove_normalized_tokens, tokenize, spellcheck, pos_tag
from .scripts.process import list_to_file, file_to_list
from .scripts.process import list_enumeration, str_to_bool, space_to_underscore
from .scripts.process import set_paragraphs, restore_paragraphs
from .scripts.process import restore_original_tokens
from .scripts.pycut import cut, insert_column
from .scripts.getOptparse import getOptionParser
import uuid
from django.conf import settings

import sys


# comparison with swedish:
# no detection with compounds for swedish


debug = settings.DEBUG

def run(opt):
    PIPE_DIR        = os.path.realpath(__file__).replace(os.path.basename(os.path.realpath(__file__)), '')
    OUTPUT_DIR      = PIPE_DIR + "output/"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    tmp_dir = settings.BASE_DIR + '/swegram_main/handle_texts/pipeline/tmp/'

    unique_filename = str(uuid.uuid4())
    original_filename = os.path.basename(opt.open)
    try:
        shutil.copy(opt.open, tmp_dir + unique_filename)
        input_file = tmp_dir + unique_filename
        basename = os.path.basename(input_file)
        basename_noext = os.path.splitext(basename)[0]

    except TypeError:
        print("No file selected, aborting.")
        shutil.rmtree(tmp_dir)
        exit(0)

    if debug:
        print('{:<20}  {:<20}'.format("Tokenizer:", opt.tokenizer))
        print('{:<20}  {:<20}'.format("Tagger:", opt.tagger))
        print('{:<20}  {:<20}'.format("Tagger model: ", opt.tagger_model))
        print('{:<20}  {:<20}'.format("Spellchecker: ", opt.spellchecker))
        print('{:<20}  {:<20}'.format("Parser: ", opt.parser))
        print('{:<20}  {:<20}'.format("Parser model: ", opt.parser_model))
        print('{:<20}  {:<20}'.format("Compounds method: ", opt.compounds_method))
        print('{:<20}  {:<20}'.format("Preserve paragraphs: ", opt.preserve_paragraphs))
        print('{:<20}  {:<20}'.format("Preserve metadata: ", opt.preserve_metadata))  # used for old version 
        print('{:<20}  {:<20}'.format("Metadata format: ", opt.metadata_format))      # used for old version
        print('{:<20}  {:<20}'.format("tmp_dir: ", tmp_dir))

    tokenized_file      = tmp_dir + basename_noext + '.tok'
    spellchecked_file   = tmp_dir + basename_noext + '.spell'
    original_token_file = tmp_dir + basename_noext + '.origtok'
    # compounds_file      = tmp_dir + basename_noext + '.cmpnd'
    tagged_file         = tmp_dir + basename_noext + '.conll'
    tmp_tokenize        = tmp_dir + basename_noext + '.toktmp'

    preserve_paragraphs = str_to_bool(opt.preserve_paragraphs)
    # preserve_metadata   = str_to_bool(opt.preserve_metadata)
    # metadata_format     = opt.metadata_format


    # These two could be used to disable tagging and parsing if an option for that
    # was made available front-end. Requires some overhaul of the analysis part though,
    # since these files wouldn't be analyzable
    #opt.tag = True
    #opt.parse = True

    # metadata_list = []

    if preserve_paragraphs:
        list_to_file(set_paragraphs(input_file), input_file)

    # if preserve_metadata:
    #     metadata_list = set_metadata(input_file, metadata_format)

    if opt.tokenize:  # Input: original file, output: tokenize.tok
        # With udpipe, tokenization has to take place twice, because:
        # If we tokenize something like TV-program, it'll be tokenized as
        # TV-
        # program
        #
        # If we then tokenize again, TV- will be split into two tokens,
        # which causes problems when we're trying to insert the original tokens
        tokenize(input_file, opt.tokenizer, tmp_dir, tokenized_file)
        list_to_file(cut('2', file_to_list(tokenized_file), False), tmp_tokenize)
        tokenize(tmp_tokenize, opt.tokenizer, tmp_dir, tokenized_file)
        # The tokenizer preserves spaces in tokens in some numerical expressions,
        # replace them with underscore for the sake of the spellchecker
        space_to_underscore(tokenized_file)
    else:
        shutil.copy(input_file, tokenized_file)


    if opt.normalize:# Input: tokenized_file, output: spellchecked_file

        spellcheck(tokenized_file, spellchecked_file, opt.spellchecker)
        sc = file_to_list(spellchecked_file)

        list_to_file(cut('2', sc, False), original_token_file)

        list_to_file(cut('3', sc, False), spellchecked_file)

        #tokenize(spellchecked_file, opt.tokenizer, tmp_dir, tokenized_file)
        #shutil.copy(tokenized_file, spellchecked_file)

    else:
        list_to_file(cut('2', file_to_list(tokenized_file), False), original_token_file)
        shutil.copy(original_token_file, spellchecked_file)

    print('tag', opt.tag, opt.tagger)
    if opt.tag:  # Input: spellchecked_file, output: tagged_file
        pos_tag(spellchecked_file, tagged_file, opt.tagger, tmp_dir)
    else:
        shutil.copy(tokenized_file, tagged_file)


    # Remove comment lines
    tagged = file_to_list(tagged_file)
    t = [line for line in tagged if not line.startswith('#')]
    list_to_file(t, tagged_file)
    

    if preserve_paragraphs:
        list_to_file(restore_paragraphs(tagged_file), tagged_file)

    restore_original_tokens(tagged_file, original_token_file)
    list_to_file(list_enumeration(tagged_file, False, '<.*>'), tagged_file)

    if not opt.normalize:
        #remove norms if normalization is not activated
        remove_normalized_tokens(tagged_file)

    if opt.custom_filename:
        shutil.move(tagged_file, PIPE_DIR + 'output/' + opt.custom_filename)
    else:
        shutil.move(tagged_file, PIPE_DIR + 'output/' + original_filename)

    # shutil.rmtree(tmp_dir)
    # os.makedirs(tmp_dir)

    if opt.custom_filename:
        if not opt.tag:
            return PIPE_DIR + 'output/' + opt.custom_filename, False  #(annotated file path, if it is eligible)
        else:
            return PIPE_DIR + 'output/' + opt.custom_filename, True
    else:
        if not opt.tag:
            return PIPE_DIR + 'output/' + original_filename, False
        else:
            return PIPE_DIR + 'output/' + original_filename, True

if __name__ == '__main__':
   options, args   = getOptionParser().parse_args()
   run(options)

# shutil.rmtree(tmp_dir)
