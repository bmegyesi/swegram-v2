#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .helpers import rm_blanks, str_to_bool
from ..config import *
from datetime import datetime
from . import filesize

from .pipeline.scripts.process import has_metadata_initial_final, metadata_content_checker, remove_feff
from .helpers import eval_str

# from .statistics import mean, median, pos_stats
from collections import Counter
import re

from .general_func import Count_features
from .readability_func import Readability_features
from .morph_func import Morph_features
from .lexical_func import Lexical_features
from .syntactic_func import Syntactic_features, is_a_ud_tree, dep_paths

# This counts erroneously split compounds as one word when calculating paragraph count if set to True, otherwise as two words.
paragraph_count_norm_based = True

class Metadata:
    metadata = {}

class Textfile:
    """
    Adjustment: 
        The following class attributes are moved to be bound with Text (Rex)
        text_size
        has_metadata:           bool
        metadata_labels:        dict
        raw_contents
        raw_contents_list       list
        normalized              bool
        meta_added              bool(meta_added used to search which texts included)

        The following attributes from Textfile works as an instance to works as a attribute in Text. 
        The following attributes are inherited to Text class
        file_id
        date_added
        activated
        eligible
        filename
        file_size
        
    """

    # def toggle_activate(self):
    #     self.activated = False if self.activated == True else True
    #     return self

    def __init__(self, filename, eligible=False, *args, **kwargs):
        super(Textfile, self).__init__()
        self.filename = os.path.basename(filename)
        self.file_id = id(self)
        self.file_size = filesize.size(os.path.getsize(filename))
        self.date_added = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.eligible = eligible
        # self.activated demonstrates if the text is current chosen to work with.
        # the default value is false
        self.activated = False

class Token:
    id = None

    text_id  = None
    token_id = None
    form     = None
    norm     = None
    lemma    = None
    upos     = None
    xpos     = None
    feats    = None
    ufeats   = None
    head     = None
    deprel   = None
    deps     = None
    misc     = None
    length   = None
    path     = None   # The path between the current token and the root.
    dep_length = None # The depth between the current token and the root.
    normalized = False

    def __init__(self):
        self.id = id(self)

    part_of_fundament = False

    # If corrected compound, include the original tokens
    compound_originals = None

    def __str__(self):
        return self.form


class Sentence:
    text_id = None
    tokens = []
    types = [] #types is a list of counters [(type1, num1),...,(type-n, num-n)]
    """features"""
    general = None
    readability = None
    ud_tree = True   #if ud_tree is false, we skip the syntactic feature extraction. 
    morph = None
    lexical = None
    syntactic = None

    def __str__(self):
        if not self.tokens:
            return ''
        sentence = str(self.tokens[0])
        for token in self.tokens[1:]:
            if token.upos != 'PUNCT':
                sentence += ' ' + str(token)
            else:
                sentence += str(token)
        return sentence


class Paragraph:
    text_id = None
    sentences = []

    """features"""
    general = None
    readability = None
    
    morph = None
    morph_average = None
    
    lexical = None
    lexical_average = None

    syntactic = None
    syntactic_average = None

    def __str__(self):
        return ' '.join([str(s) for s in self.sentences])
    
    

class Text(Textfile):
    text = [] # is it also the list of text lines?
    paragraphs = []
    sentences = []
    
    lang = None #
    filename = None
    id = 0
    metadata = []        #metadata is data referring to this very text
    metadata_labels = [] #metadata_labels are labels extracted from the beginning of the text
    zip_meta_labels = []
    

    paragraphs = [] # contains ints of lengths for each paragraph
    #paragraph_sents = []


    # normalized = False
    # parsed = False
    

    """features"""
    general = None
    readability = None
    morph = None
    morph_average = None

    lexical = None
    lexical_averge = None

    syntactic = None
    syntactic_average = None

    
    def toggle_activate(self):
        self.activated = False if self.activated == True else True
        return self
    

    content_words = [] # non-MAD,PAD,MID words

    def __init__(self, filename, eligible, normalized, parsed, has_label=False, \
                 labels={}, meta_added=False, *args, **kwargs):
        super(Text, self).__init__(filename, eligible)
        self.id = id(self)
        self.eligible = eligible
        self.activated = False
        self.normalized = normalized
        self.parsed = parsed
        self.has_label = has_label
        self.meta_added = meta_added
        self.labels = labels
        self.raw_contents_list = list()
    
    def __str__(self):
        return '\n  '.join([str(p) for p in self.paragraphs])

    

def create_token(lang, t, parsed, compound_originals=False):
    token = Token()
    token.text_id  = t[0]
    token.compound_originals = compound_originals
    token.token_id = t[1]
    token.form     = t[2].strip()
    if compound_originals:
        token.norm     = "_"
        token.lemma    = "_"
        token.upos     = "_"
        token.xpos     = "_"
        token.feats    = "_"
        token.ufeats   = "_"
        token.head     = "_"
        token.deprel   = "_"
        token.deps     = "_"
        token.misc     = "_"
    else:
        token.norm     = t[3]
        token.lemma    = t[4]
        if not parsed:
            token.upos     = "_"
            token.xpos     = "_"
            token.feats    = "_"
            token.ufeats   = "_"
            token.head     = "_"
            token.deprel   = "_"
            token.deps     = "_"
            token.misc     = "_"
        else:
            token.upos     = t[5]
            token.xpos     = t[6]
            token.feats    = t[7]   #??? the output of file: ufeats is placed before feats
            if lang == 'en':
                token.head     = t[8]   
                token.deprel   = t[9]
                token.deps     = t[10]
                token.misc     = t[11]
            else:
                token.ufeats   = t[8]    # the difference between English and Swedish            
                token.head     = t[9]
                token.deprel   = t[10]
                token.deps     = t[11]
                token.misc     = t[12]

    token.length = len(token.norm)

    if token.form != token.norm:
        token.normalized = True

    return token       

def create_annotated_paragraphs(text, lang, parsed):
    paragraphs = []
    p = Paragraph()
    para_lines = []
    para_index = None
    while text:
        para_line = text.pop(0).lstrip().strip()
        para_index_check = para_line.split('\t')[0].lstrip().strip()
        if para_index_check != para_index and para_lines:
            para_index = para_index_check
            p.sentences = create_annotated_sentences(para_lines, lang, parsed)
            if p.sentences:
                """features for paragraphs"""
                p = get_paragraph_stats(lang, p, parsed)
                paragraphs.append(p)
            p = Paragraph()
            para_lines = []
            
        elif para_index_check != para_index and not para_lines:
            para_index = para_index_check

        para_lines.append(para_line)
    if para_lines:
        p.sentences = create_annotated_sentences(para_lines, lang, parsed)
        if p.sentences:
            p = get_paragraph_stats(lang, p, parsed)
            paragraphs.append(p)

    
    return paragraphs

def create_paragraphs(text, lang, parsed):
    paragraphs = []
    p = Paragraph()
    para_lines = []
    if text.raw_contents_list:
        para_index = text.raw_contents_list[0].lstrip().split('.')[0]
        text_lines = rm_blanks(text.raw_contents_list) + ['$END_MARKER$']  #to add an end marker to include the last paragraph for looping
    else:
        print('Error. Text is empty.')
        assert False 
    for line in text_lines:
        if not line.strip():
            para_lines.append(line)
        else:
            index = line.strip().lstrip().split('.')[0]
            if index == para_index:
                para_lines.append(line)
            else:
                p.sentences = create_sentences(para_lines, lang, parsed)
                if p.sentences:
                    p = get_paragraph_stats(lang, p, parsed)
                    paragraphs.append(p)
                p = Paragraph()
                para_index = index
                para_lines = [line]
    return paragraphs              


def create_annotated_sentences(content, lang, parsed):
    sentences = []
    sentence = Sentence()
    sentence.tokens = []
    sent_index = None
    while content:
        split_line = content.pop(0).split('\t')
        if len(split_line) < 3:
            continue
        # elif len(split_line) == 3:
        #     token = create_token(lang, split_line, True)
        #     sentence.tokens.append(token)
        # else:
        #     token = create_token(lang, split_line)
        #     sentence.tokens.append(token)
        sent_index_check = split_line[0]
        if sent_index_check != sent_index and sentence.tokens:
            sent_index = sent_index_check
            sentence = get_sentence_stats(lang, sentence, parsed)
            if parsed:
                if not is_a_ud_tree(sentence):
                    sentence.ud_tree = False
                    sentences.append(sentence)
                    sentence = Sentence()
                    sentence.tokens = []

                else:
                    dep_paths_list = dep_paths(sentence)
                    for index, token in enumerate(sentence.tokens):
                        token.dep_length = len(dep_paths_list[index])-1
                        token.path = " <-- ".join(dep_paths_list[index])

                    sentence.syntactic = vars(Syntactic_features(sentence))
            sentences.append(sentence)
            sentence = Sentence()
            sentence.tokens = []

        elif sent_index_check != sent_index and not sentence.tokens:
            sent_index = sent_index_check

        if len(split_line) == 3:
            token = create_token(lang, split_line, parsed, True)
        else:
            token = create_token(lang, split_line, parsed)
        sentence.tokens.append(token)
    
    if sentence.tokens:
        sentence = get_sentence_stats(lang, sentence, parsed)
        if parsed:
            if not is_a_ud_tree(sentence):
                sentence.ud_tree = False
            else:
                dep_paths_list = dep_paths(sentence)
                for index, token in enumerate(sentence.tokens):
                    token.dep_length = len(dep_paths_list[index])-1
                    token.path = " <-- ".join(dep_paths_list[index])
                sentence.syntactic = vars(Syntactic_features(sentence))
        sentences.append(sentence)
    return sentences
        
        


def create_sentences(content, lang, parsed):
    line_length = 12 if lang=='en' else 13     
    sentences = []
    sentence = Sentence()
    sentence.tokens = []
    for x in range(len(content)):
        split_line = content[x].split("\t")
        if len(split_line) == line_length:
            token = create_token(lang, split_line, parsed)
            sentence.tokens.append(token)
        elif len(split_line) == 3:
            token = create_token(lang, split_line, parsed, True)
            sentence.tokens.append(token)
        elif split_line[0] == '\n': #'\n' is a breaker between sentences when it appears in the beginning of the sentence
            if sentence.tokens:
                # Check for fundament
                sentence = get_sentence_stats(lang, sentence, parsed)
                if parsed:
                    if not is_a_ud_tree(sentence):
                        sentence.ud_tree = False #we ask the user to take care of the text if the parsing is not correct
                        sentences.append(sentence)
                        sentence = Sentence()
                        sentence.tokens = []
                        continue
                      
                    dep_paths_list = dep_paths(sentence)
                    for index, token in enumerate(sentence.tokens):
                        token.dep_length = len(dep_paths_list[index])-1
                        token.path = " <-- ".join(dep_paths_list[index])

                    sentence.syntactic = vars(Syntactic_features(sentence))
                sentences.append(sentence)
                sentence = Sentence()
                sentence.tokens = []
    return sentences


def import_annotated_text(request, lang, path, label):
    checkNormalization = str_to_bool(request.POST.get('checkNormalization', 'false'))
    checkPOS = str_to_bool(request.POST.get('checkPOS', 'false'))

    has_not_error, error_msgs = uploaded_file_checker(path, lang, True, checkNormalization, checkPOS)
    if has_not_error:
        text = create_text(lang, path, label, True, checkNormalization, checkPOS, annotated=True)
        return True, text
    else:
        return False, error_msgs


def get_sentence_stats(lang, sentence, parsed):
    if lang == 'sv':
        for x in range(len(sentence.tokens)):
            t = sentence.tokens[x]
            if 'VerbForm=Fin' in t.ufeats:
                for tok in sentence.tokens[:x]:
                    tok.part_of_fundament = True
                break
    sentence.types = Counter([token.norm for token in sentence.tokens])
    sentence.text_id = sentence.tokens[0].text_id
    sentence.general = vars(Count_features(sentence, lang, level='sent'))
    sentence.readability = vars(Readability_features(sentence, lang, level='sent'))

    if parsed:
        sentence.morph = vars(Morph_features(sentence, lang, level='sent'))   #use vars() to serialize the object to json data
        sentence.lexical = vars(Lexical_features(sentence, lang, level='sent'))
    
    return sentence   


def get_paragraph_stats(lang, p, parsed):
    """features for paragraphs"""
    p.general = vars(Count_features(p, lang=lang, level='para'))
    p.readability = vars(Readability_features(p, lang, level='para')) # Function here to be implemented
    if parsed:
        p.morph = vars(Morph_features(p, lang, level='para'))
        p.morph_average = vars(Morph_features(p, lang, algorithm='average', level='para'))

        p.lexical = vars(Lexical_features(p, lang=lang, level='para'))
        p.lexical_average = vars(Lexical_features(p, lang=lang, algorithm='average', level='para'))

        p.syntactic = vars(Syntactic_features(p, level='para'))
        p.syntactic_average = vars(Syntactic_features(p, algorithm='average', level='para'))
    return p


def get_text_stats(lang, text, parsed):
    """features for text"""
    text.general = vars(Count_features(text, lang=lang, level='text'))
    text.readability = vars(Readability_features(text, lang, level='text'))
    
    if parsed:
        text.morph = vars(Morph_features(text, lang, level='text'))
        text.morph_average = vars(Morph_features(text, lang, algorithm="average", level='text'))

        text.lexical = vars(Lexical_features(text, lang=lang, level='text'))
        text.lexical_average = vars(Lexical_features(text, lang=lang, algorithm="average", level="text"))

        text.syntactic = vars(Syntactic_features(text, level='text'))
        text.syntactic_average = vars(Syntactic_features(text, algorithm="average", level="text"))

    return text


def import_text(request, lang, label, path, eligible, check_if_normalizd=False):
    checkNormalization = str_to_bool(request.POST.get('checkNormalization', 'false'))
    checkPOS = str_to_bool(request.POST.get('checkPOS'))
    text = create_text(lang, path, label, eligible, checkNormalization, checkPOS)
    
    return text
    

class Labels:
    """
    This class collects all properties associated with text attributes
    
    data structure for labels here
    {
        (label_type tag_delimiter label_value) : [
            text_id
        ]
    }
    This class is mainly used for retreiving the text_id given the labels
    """

    def __init__(self, labels={}):
        self.labels = labels
    
    def _get_text_ids_by_tag(self, tag, value=False):
        """
        return a list of text ids given the tag
        if value is set, the text ids with the exact pair of tag and value are returned
        """
        text_ids = []
        for key in self.labels:
            source_tag, source_value = key.split(METADATA_DELIMITER_LEBAL)
            if value:
                if source_tag == tag and source_value == value:
                    text_ids.extend(self.labels[key])
            else:
                if source_tag == tag:
                    text_ids.extend(self.labels[key])
        return text_ids
    

    def _get_tag_value(self):
        """
        return a dict to indicate the possible pairs of tag and values
        """
        tag_values = {}
        for key in self.labels:
            tag, value = key.split(METADATA_DELIMITER_TAG)
            tag_values[tag] = value
        return tag_values
                
    
    def _add(self, text_id, labels): #labels structure {tag1:value1, tag2:value2, ..., tagn:valuen}
        """add a text_id with based on label_type and label_value into the object"""
        for label in labels:
            key = METADATA_DELIMITER_TAG.join([label, labels[label]])
            if key in self.labels:
                self.labels[key].append(text_id)
            else:
                self.labels[key] = [text_id]
    

    def _remove(self, text_id):
        """
        the labels should be removed when the text is no longer stored in session
        the text can be removed when we need to have an updated one
        """
        for key in self.labels:
            if text_id in self.labels[key]:
                self.labels[key].remove(text_id)
        

def create_text(lang, filename, label, eligible, checkNormalization, checkPOS, annotated=False):
    text = Text(filename, eligible, checkNormalization, checkPOS)
    text.id = id(text)
    text.lang = lang
    
    with open(filename, 'r', encoding='utf-8-sig') as f:
        line = f.readline()
        while line:
            line = line.replace('\r', '')
            text.raw_contents_list.append(line)
            line = f.readline()
        if label:
            text.has_label = True
            text.labels = label
            # we ignore the attribute of meta_added
    
    if rm_blanks(text.raw_contents_list):
        text.raw_contents_list = rm_blanks(text.raw_contents_list)
        """create tokens and sentences given the annotated text"""
        if annotated:
            # for line in text.raw_contents_list:
            #     if line.strip():
            #         if len(line.split('\t')) < 10:
            #             print('line', line)
            text.paragraphs = create_annotated_paragraphs([line for line in text.raw_contents_list if line.strip()], lang, checkPOS)
        else:
            text.paragraphs = create_paragraphs(text, lang, checkPOS)
        text.sentences = [sent for p in text.paragraphs for sent in p.sentences]
        text = get_text_stats(lang, text, checkPOS)
    return text

def par_sent_index_checker(index):
    if not re.fullmatch(r'[1-9]\d*\.[1-9]\d*', index.strip()):
        return {    
          'error_type': 'COLUMN_INDEX_ERROR',
          'error_prompt': 'Index for paragraph and sentence is not correct.',
          'content': index
        }
    return True

def token_index_checker(index):
    for i in index.strip().split('-'):
        if not re.fullmatch(r'\d+', i):
            return {
              'error_type': 'COLUMN_INDEX_ERROR',
              'error_prompt': 'Index for token is not correct',
              'content': index
            }
    return True

def head_checker(head, tabs, line_index):
    error = {
      'line_number': line_index,
      'error_type': 'COLUMN_HEAD_ERROR',
      'error_prompt': 'The head is not a non-negative integer but got %s' % (head),
      'content': ' '.join(tabs)
    }
    try:
        if int(head) >= 0:
            return True
        else:
            return error
    except Exception:
        return error
    
def empty_checker(input, input_type, tabs, line_index):
    if input.strip() == '':
        return {
          'line_number': line_index,
          'error_type': 'COLUMN_%s_ERROR' % (input_type.upper()),
          'error_prompt': 'Column %s is empty.' % (input_type),
          'content': '\t'.join(tabs)
        }
    return True

def norm_checker(form, norm, tabs, line_index):
    if form != '_' and norm == '_':
        return {
          'line_number': line_index,
          'error_type': 'COLUMN_NORM_ERROR',
          'error_prompt': 'Form %s is not normalized.' % (form),
          'content': '\t'.join(tabs)
        }
    return True

def pos_checker(pos, tagset_range, tagset_type, tabs, line_index):
    if pos.strip().lstrip() not in tagset_range:
        return {
          'line_number': line_index,
          'error_type': 'COLUMN_%s_ERROR' % (tagset_type.upper()),
          'error_prompt': '%s does not contain PoS tag %s' % (tagset_type.upper(), pos),
          'content': '\t'.join(tabs)
        }
    return True

def ufeats_checker(feats, ufeats, tabs, line_index):
    errors = []
    for feat in feats.split('|'):
        if feat not in ufeats:
            errors.append({
              'line_number': line_index,
              'error_type':'COLUMN_UFEATS_ERROR',
              'error_prompt':'Feature %s is not included for Swedish.' % feat,
              'content': '\t'.join(tabs)
            })
    return True if errors == [] else errors

def feats_checker(feats, feat_dict, tabs, line_index):
    """do more investgation to check what kind of feat types and feat value they can be"""
    errors = []
    for feat in feats.split('|'):
        if '_' == feat:
            continue
        else:
            try:
                key, value = feat.split('=')
                if key not in feat_dict:
                    errors.append({
                      'line_number': line_index,
                      'error_type': 'COLUMN_FEATS_ERROR',
                      'error_prompt': 'The feature label %s is unknown.' % (key),
                      'content': '\t'.join(tabs)
                    })
                else:
                    if value not in feat_dict[key]:
                        errors.append({
                          'line_number': line_index,
                          'error_type': 'COLUMN_FEATS_ERROR',
                          'error_prompt': 'The feature value %s is unknown to feature label %s' % (value, key),
                          'content': '\t'.join(tabs)
                        })
            except Exception:
                errors.append({
                    'line_number': line_index,
                    'error_type': 'COLUMN_FEATS_ERROR',
                    'error_prompt': 'The feature structure %s is not standard.' % (feat),
                    'content': '\t'.join(tabs)
                })
    return True if errors == [] else errors

def deprel_checker(rel, rels, tabs, line_index):
    if rel.strip().lstrip() not in rels: 
        return {
          'line_number': line_index,
          'error_type': 'COLUMN_DEPREL_ERROR',
          'error_prompt': 'Dependency relation %s is unknown.' % (rel),
          'content': '\t'.join(tabs)
        }
    return True


def get_next_line(current_line, f):
    new_line = f.readline()
    while new_line == current_line:
        new_line = f.readline()
    return new_line, f

def uploaded_file_checker(path, lang, annotated, normalized, parsed, line_index=1):
    """
    Description of the function: 
      This function ckecks the file meets the requirements
      of the system. There are two types of files through this checker.
      Any line that starts with hashtagg is to be excluded. 
    
    The path refers to where the file is stored.
    
    We assume that the file given the path has and only has one text.
    According to the setting, we categorize the text into annotated one and unannotated one.
    For the part of unannotated one, the check will only check possible metadata line
    For the part of annotated one, the checker will go through the data given the setting here.
    
    Here are the schemas when an annotated text goes through with the given setting 
    setting:      normalization         PoS tagging & Parsing
    Yes           
    No

    error_msg: [
      {
        line_number: 1,
        error_type: ‘unknown pos tag’,
        sentence: ‘an example sentence.’,
        annotation: ‘PART’
      }
    ]	
    
    ERROR_TYPE:
    1. METADATA_ERROR (available for all)
      a. multiple metadata labels in the same metadata line
      b. Unknown format for metadata line
    2. COLUMN_NUMBER_ERROR (available for annotated text)
        # if COLUMN_NUMBER_ERROR appears, the checker will not continue the rest tests for the same line
                      unnormalized        normalized
        a. unparsed   5                   5     
        b. parsed     (en: 12, sv: 13)    (en: 12, sv: 13)
      1. COLUMN_INDEX_ERROR: The first column is to have PARAGRAPH_INDEX.SENTENCE_INDEX (INDEX is to be an integer.)
      2. COLUMN_INDEX_ERROR: The second column is to have TOKEN_INDEX (INDEX is to be an integer.)
      3. COLUMN_FORM_ERROR: The form column is to have a non-empty string 
      4. COLUMN_NORM_ERROR: The norm column is to have a non-empty string; The form is not normalized iff norm is an underline while form is not
      5. COLUMN_LEMMA_ERROR: The lemma column is to have a non-empty string
      6. COLUMN_UPOS_ERROR: Unknown universal PoS tag
      7. COLUMN_XPOS_ERROR: Unknown X-PoS tag
      8. COLUMN_FEATS_ERROR: Unknown features
      9. COLUMN_UFEATS_ERROR: Unknown Swedish features
      9. (sv+1). COLUMN_HEAD_ERROR: The head column is to have an integer
      10. (sv+1). COLUMN_DEPREL_ERROR: Unknown dependency relations
      11. (sv+1). COLUMN_DEPS_ERROR: The deps column is to have a non-empty string
      12. (sv+1). COLUMN_MISC_ERROR: The misc column is to have a non-empty string 

    3. SENTENCE_UD_TREE_ERROR: Not a standard UD tree given the annotation.
    """
    
    has_not_error, error_msgs = True, []    
    with open(path, mode='r', encoding='utf-8-sig') as f:
        sentence = [] # to check if the annotated sentence has a standard ud tree.
        line = f.readline()
        sentence_index = None
        while line:
            line = remove_feff(line)
            if line.strip() == '':
                line_index += 1
                line = f.readline()
                continue

            # check if it is a comment
            if line.startswith('#'):
                line_index += 1
                line, f = get_next_line(line, f)
                continue
            
            # check if it is a metadata line
            has_label, metadata_content = has_metadata_initial_final(line)
            if has_label:
                has_error, error_dict = metadata_content_checker(metadata_content)
                if has_error:
                    has_not_error = False
                    error_dict['line_number'] = line_index
                    error_msgs.append(error_dict)
                line_index += 1
                line = f.readline()
                continue
            
            if annotated is False:
                line_index += 1
                line = f.readline()
                print('annotation is False')
                continue
    
            
            tabs = line.strip().lstrip().split('\t')
            
            if sentence_index is None:
                sentence_index = tabs[0].strip().lstrip()
          
            # check the ud tree format
            if parsed is True and sentence_index and sentence and sentence_index != tabs[0].strip().lstrip():
                try:              
                    check_ud_tree = is_a_ud_tree(sentence, upload_annotated=True)
                    if check_ud_tree is not True:
                        has_not_error = False
                        error_msgs.append(
                          {
                            'line_number': '-'.join([str(line_index-len(sentence)), str(line_index-1)]),
                            'error_type': 'UD_TREE_ERROR',
                            'error_prompt': 'It is not a standard ud tree. %s' % check_ud_tree,
                            'content': ' '.join([token.form + ' ' + str(token.head) for token in sentence])
                          }
                        )
                except Exception:
                    has_not_error = False
                    error_msgs.append(
                      {
                        'line_number': '-'.join([str(line_index-len(sentence)), str(line_index-1)]),
                        'error_type': 'UD_TREE_ERROR',
                        'error_prompt': 'It is not a standard ud tree.',
                        'content': ' '.join([token.form + ' ' + str(token.head) for token in sentence])
                      }
                    )    
                sentence = []
                sentence_index = tabs[0].strip().lstrip()

            
            # check column number
            if line.strip():
                tab_num = 12 if lang == 'en' else 13
                if len(tabs) not in [3, tab_num]:
                    has_not_error = False
                    error_msgs.append(
                      {
                        'line_number': line_index,
                        'error_type': 'COLUMN_NUMBER_ERROR',
                        'error_prompt': 'Expected to have %d columns, but got %d instead.' % (tab_num, len(tabs)),
                        'content': line.strip().lstrip() 
                      }
                    )
                    line_index += 1
                    line = f.readline()
                    continue

            # start to check the column type and its content
            # if this is a compound
            par_sent_index, token_index, form = tabs[:3]
            
            check_par_sent_index = par_sent_index_checker(par_sent_index)
            if check_par_sent_index is not True:
                has_not_error = False
                check_par_sent_index['line_number'] = line_index
                error_msgs.append(check_par_sent_index)
            
            check_token_index = token_index_checker(token_index)
            if check_token_index is not True:
                has_not_error = False
                check_token_index['line_number'] = line_index
                error_msgs.append(check_token_index)
             
            check_form = empty_checker(form, 'form', tabs, line_index)
            if check_form is not True:
                has_not_error = False
                error_msgs.append(check_form)
            
            if len(tabs) == 3:
                line_index += 1
                line = f.readline()
                # if parsed is True: # The compound does not affect if it is a standard ud tree
                #     sentence.append(create_token(lang, tabs, True))
                continue
            
            norm, lemma = tabs[3:5]
            check_norm_empty = empty_checker(norm, 'norm', tabs, line_index)
            if check_norm_empty is not True:
                has_not_error = False
                error_msgs.append(check_norm_empty)
            if normalized:
                check_norm = norm_checker(norm, form, tabs, line_index)
                if check_norm is not True:
                    has_not_error = False
                    error_msgs.append(check_norm)
            
            check_lemma = empty_checker(lemma, 'lemma', tabs, line_index)
            if check_lemma is not True:
                has_not_error = False
                error_msgs.append(check_lemma)
            
            if parsed is False:
                line_index += 1
                line = f.readline()
                continue
            
            upos, xpos = tabs[5:7]
            check_upos = pos_checker(upos, UD_TAGS, 'upos', tabs, line_index)
            if check_upos is not True:
                has_not_error = False
                error_msgs.append(check_upos)
            if lang == 'en':
                check_xpos = pos_checker(xpos, PT_TAGS, 'xpos', tabs, line_index)
            elif lang == 'sv':
                check_xpos = pos_checker(xpos, SUC_TAGS, 'xpos', tabs, line_index)
            if check_xpos is not True:
                has_not_error = False
                error_msgs.append(check_xpos)
              
            if lang == 'sv': # to follow the order when checking
                check_ufeats = ufeats_checker(tabs[-6], UFEATS, tabs, line_index)
                if check_ufeats is not True:
                    error_msgs.extend(check_ufeats)

            feats, head, deprel, deps, misc = tabs[-5:]

            check_feats = feats_checker(feats, FEATS, tabs, line_index)
            if check_feats is not True:
                has_not_error = False
                error_msgs.extend(check_feats)

            check_head = head_checker(head, tabs, line_index)
            if check_head is not True:
                has_not_error = False
                error_msgs.append(check_head)
            
            check_deprel = deprel_checker(deprel, DEPRELS, tabs, line_index)
            if check_deprel is not True:
                has_not_error = False
                error_msgs.append(check_deprel)
            
            check_deps = empty_checker(deps, 'deps', tabs, line_index)
            if check_deps is not True:
                has_not_error = False
                error_msgs.append(check_deps)
            
            check_misc = empty_checker(misc, 'misc', tabs, line_index)
            if check_misc is not True:
                has_not_error = False
                error_msgs.append(check_misc) 
            
            # to store Token in the sentence
            # print('token to be added', create_token(lang, tabs, parsed).form)
            sentence.append(create_token(lang, tabs, parsed))
            line_index += 1
            line = f.readline()
            # print('new line', line)
            continue
    
    return has_not_error, error_msgs
