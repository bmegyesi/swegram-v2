#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import sys
# from optparse import OptionParser
# import tempfile
import shutil

from django.utils.functional import empty
from .scripts.process import tokenize, spellcheck, compound_check, pos_tag #(compound_check is not used)
from .scripts.process import list_to_file, file_to_list, separate_pos  # (separate_pos is not used for sv)
from .scripts.process import enumerate_tokens, list_enumeration, str_to_bool, space_to_underscore
from .scripts.process import set_paragraphs, restore_paragraphs
from .scripts.process import set_metadata, restore_metadata
from .scripts.pycut import cut, insert_column
import uuid
from django.conf import settings

from .scripts.compounds import find_compounds, insert_originals
from .scripts.getOptparse import getOptionParser

debug = settings.DEBUG

"""
1. checker (to add)
    format checker 
    size checker (done from frontend)
    file checker (need to be implemented)
"""
def run(opt):
    PIPE_DIR        = os.path.realpath(__file__).replace(os.path.basename(os.path.realpath(__file__)), '')
    OUTPUT_DIR      = PIPE_DIR + "output/"

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

    tokenized_file      = tmp_dir + basename_noext + '.tok'
    spellchecked_file   = tmp_dir + basename_noext + '.spell'
    compounds_file      = tmp_dir + basename_noext + '.cmpnd'
    tagged_file         = tmp_dir + basename_noext + '.conll'

    preserve_paragraphs = str_to_bool(opt.preserve_paragraphs)
    # preserve_metadata   = str_to_bool(opt.preserve_metadata)
    # metadata_format     = opt.metadata_format

    # metadata is also used as the indicator of text boundary in an uploaded file.
    # before the file annotated, metadata is extracted.
    # metadata_list = []

    if debug:
        print('{:<20}  {:<20}'.format("Tokenizer:", opt.tokenizer))
        print('{:<20}  {:<20}'.format("Tokenize:", opt.tokenize))
        print('{:<20}  {:<20}'.format("Tagger:", opt.tagger))
        print('{:<20}  {:<20}'.format("Tag:", opt.tag))
        print('{:<20}  {:<20}'.format("efselab model: ", opt.tagger_model))
        print('{:<20}  {:<20}'.format("Spellchecker: ", opt.spellchecker))
        print('{:<20}  {:<20}'.format("Parser: ", opt.parser))
        print('{:<20}  {:<20}'.format("Parse: ", opt.parse))
        print('{:<20}  {:<20}'.format("Maltparser model: ", opt.parser_model))
        print('{:<20}  {:<20}'.format("Compounds method: ", opt.compounds_method))
        print('{:<20}  {:<20}'.format("Preserve paragraphs: ", opt.preserve_paragraphs))
        # print('{:<20}  {:<20}'.format("Preserve metadata: ", opt.preserve_metadata))
        # print('{:<20}  {:<20}'.format("Metadata format: ", opt.metadata_format))
        print('{:<20}  {:<20}'.format("tmp_dir: ", tmp_dir))

    

    if preserve_paragraphs:
        list_to_file(set_paragraphs(input_file), input_file)

    # if preserve_metadata:   # we need to change this to represent the metadata
    #     metadata_list = set_metadata(input_file, metadata_format)

    if opt.tokenize:  # Input: original file, output: tokenize.tok
        tokenize(input_file, opt.tokenizer, tmp_dir, None)
        # The tokenizer preserves spaces in tokens in some numerical expressions,
        # replace them with underscore for the sake of the spellchecker
        space_to_underscore(tokenized_file)
    else:
        shutil.copy(input_file, tokenized_file)


    if opt.normalize:# Input: tokenized_file, output: spellchecked_file
        spellcheck(tokenized_file, spellchecked_file, opt.spellchecker)
    else:
        shutil.copy(tokenized_file, spellchecked_file)


    if opt.normalize and opt.tag: # Input: spellchecked_file (tagger) and tagged_file (compounds checker)
                      # output: compounds_file

        pos_tag(spellchecked_file, None, opt.tagger, tmp_dir)
        compounds_list = find_compounds(tagged_file)
        #compounds_list = find_compounds(spellchecked_file)

        spellchecked = file_to_list(spellchecked_file)
        originals    = file_to_list(tokenized_file)

        # Replace split compounds with corrected ones
        for c in compounds_list:
            new_string = spellchecked[c].strip() + spellchecked[c + 1]
            del spellchecked[c]
            del spellchecked[c]
            spellchecked.insert(c, new_string)
        list_to_file(spellchecked, spellchecked_file)


        # Tag again using the new compounds
        pos_tag(spellchecked_file, None, opt.tagger, tmp_dir)

        # Insert original tokens and reenumerate        
        list_to_file(insert_originals(file_to_list(tagged_file), originals, compounds_list), compounds_file)

    else:
        #compounds_list = enumerate_tokens(tokenized_file, spellchecked_file, opt.normalize)   
        #list_to_file(compounds_list, compounds_file)
        shutil.copy(spellchecked_file, compounds_file)
        
    if opt.tag and not opt.normalize:  # Input: compounds_file, output: tagged_file
        pos_tag(compounds_file, None, opt.tagger, tmp_dir)

    else:
        shutil.copy(compounds_file, tagged_file)
    

    if preserve_paragraphs:
        print('restore paragraphs')
        list_to_file(restore_paragraphs(tagged_file), tagged_file)

    # if preserve_metadata:
    #     list_to_file(restore_metadata(tagged_file, metadata_list), tagged_file)

    if opt.tag:
        list_to_file(list_enumeration(tagged_file, False, '<.*>'), tagged_file)
    else:
        updated_tagged = []
        paragraph_index, sentence_index, token_index = 1, 1, 0
        first_newline, second_newline = False, False
        def index_helper(first_newline, second_newline, token_index, paragraph_index, sentence_index):
            if second_newline:
                paragraph_index += 1
                sentence_index = 1
                token_index = 0
                first_newline, second_newline = False, False
            elif first_newline:
                second_newline = True
                sentence_index += 1
                token_index = 0
            else:
                first_newline = True
            return first_newline, second_newline, token_index, paragraph_index, sentence_index

        if opt.normalize:
            for form, norm in zip(restore_paragraphs(tokenized_file), restore_paragraphs(spellchecked_file)):
                if form.strip():
                    token_index += 1
                    index = '.'.join([str(paragraph_index), str(sentence_index)])
                    line = '\t'.join([index, str(token_index), form.strip(), norm.strip(), *['_' for _ in range(8)]]) + '\n'
                    updated_tagged.append(line)
                else:
                    first_newline, second_newline, token_index, paragraph_index, \
                    sentence_index = index_helper(first_newline, second_newline, \
                      token_index, paragraph_index, sentence_index)
                    updated_tagged.append('\n')
        else:
            for form in file_to_list(tagged_file):
                if form.strip():
                    token_index += 1
                    index = '.'.join([str(paragraph_index), str(sentence_index)])
                    line = '\t'.join([index, str(token_index), form.strip(), *['_' for _  in range(9)]]) + '\n'
                    updated_tagged.append(line)
                else:
                    first_newline, second_newline, token_index, paragraph_index, \
                    sentence_index = index_helper(first_newline, second_newline, \
                      token_index, paragraph_index, sentence_index)
                    updated_tagged.append('\n')
                    
                    
                                        
        # for l in file_to_list(tagged_file):
        #     if l.strip():
        #         print('line', l)
        #         line = l.split('\t')
        #         token_index, form = line[:2]
        #         if token_index == '1' and form == 'PARAGRAPH':
        #             paragraph_index += 1
        #             updated_tagged.append('\n')
        #             continue
        #         if token_index == '1':
        #             sentence_index += 1
        #             updated_tagged.append('\n')
        #         updated_tagged.append('\t'.join([str(paragraph_index)+'.'+str(sentence_index), l]))
          
        # for line in file_to_list(tagged_file):
        #     spl = line.split("\t")
        #     if len(spl) > 5:
        #         if spl[5] != '_':
        #             new_line = '\t'.join(spl[:4]) + "\t_\t_\t_\t_\t_\t_\t_\t_\n"
        #             updated_tagged.append(new_line)
        #         else:
        #             updated_tagged.append('\t'.join(spl))
        #     else:
        #         updated_tagged.append('\t'.join(spl))

        list_to_file(updated_tagged, tagged_file)

    if opt.columns:
        list_to_file(cut(opt.columns, file_to_list(tagged_file), False), tagged_file)

    # Move the finished file to the output dir
    # shutil.copy(tagged_file, OUTPUT_DIR) #(Rex: not to move the file to output fold)


    # This method is temporary, i'll integrate this somewhere else later
    # It removes compounds from the NORM column
    def remove_form_cmpnd(input_file):
        in_file = file_to_list(input_file)
        new_list = []
        for x in range(len(in_file)):
            if len(in_file[x].split("\t")) > 1:
                if "-" in in_file[x].split("\t")[1]:
                    new_line = '\t'.join(in_file[x].split("\t")[:2]) + "\t_\t" + \
                    '\t'.join([a for a in in_file[x].split("\t")[3:]])
                    new_list.append(new_line)
                else:
                    new_list.append(in_file[x])
            else:
                new_list.append(in_file[x])
        return new_list

    empty_norm = []
    for line in file_to_list(tagged_file):
        empty_norm.append('_')
        # from to index

    if not opt.normalize and opt.tag:
        list_to_file(insert_column(empty_norm, file_to_list(tagged_file), 3), tagged_file)
    
    list_to_file(separate_pos(tagged_file), tagged_file)

    if opt.custom_filename:
        shutil.move(tagged_file, PIPE_DIR + 'output/' + opt.custom_filename)
    else:
        shutil.move(tagged_file, PIPE_DIR + 'output/' + original_filename)
    
    # Delete temporary files tmp
    # tmp_dir = settings.BASE_DIR + '/swegram_main/handle_texts/pipeline/tmp/'
    
    
    # shutil.rmtree(tmp_dir)
    # os.makedirs(tmp_dir)


    if opt.custom_filename:
        if not opt.tag:
            return PIPE_DIR + 'output/' + opt.custom_filename, False
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
