#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script summarizes all features invovled in this pipeline
The features can be seen in different dimensions:

dimension 1: word, sentence, paragraph, text, texts. Texts here refers to selected texts from the user
dimension 2: general, readability, lexical, morphological, syntactic features
dimension 3: scalar, average(including mean and median based on sentence level)

"""
from swegram_main.handle_texts.helpers import eval_str
from .general_func import Count_features, merge_defaultdicts
from .readability_func import Readability_features
from .lexical_func import Lexical_features
from .morph_func import Morph_features
from .syntactic_func import Syntactic_features

from django.http import JsonResponse
from collections import OrderedDict

from .statistics import get_text_list
from ..config import SUC_TAGS, PT_TAGS, PAGE_SIZE
import string
import json

from ..models import TextStats, Text, Paragraph, Sentence


def get_features_helper_on_tokenization(content, lang, level, removed_features=[], overview=False):
    """
    overview is true when we need to create|compute features given the newly selected texts
    """
    ### general feature extraction
    if overview:
        contents_count = vars(Count_features(content, lang=lang, level=level))
        content.general = contents_count
    else:
        contents_count = eval_str(content.general)


    count_features = []
    for feat in contents_count['feats'].keys():
        if feat in removed_features:
            continue
        scalar = contents_count['feats'][feat] if contents_count['feats'][feat] else 0
        try:
            count_features.append({
              'name': feat, 'scalar': scalar, \
              'mean': contents_count['average'][feat]['mean'], \
              'median': contents_count['average'][feat]['median']
            })
        except KeyError:
            count_features.append({
              'name': feat, 'scalar': scalar
            })
    
    for feat in [feat for feat in contents_count['average'].keys() if feat not in contents_count['feats'].keys() if feat not in removed_features]:
        count_features.append({
          'name': feat, 'mean': contents_count['average'][feat]['mean'],
          'median': contents_count['average'][feat]['median']
        })
    
    ###readability feature extraction
    ### three features of five readability are based on only tokenization
    if overview:
        content_readability = vars(Readability_features(content, lang=lang, level=level))
    else:
        content_readability = eval_str(content.readability)
    readability_features = []
    for feat in content_readability['feats'].keys():
        if feat in removed_features:
            continue
        if level != 'sent':
            readability_features.append({
              'name':feat, 'scalar':content_readability['feats'][feat], \
              'mean':content_readability['average'][feat]['mean'], \
              'median':content_readability['average'][feat]['median']
            })
        else:
            readability_features.append({
              'name':feat, 'scalar':content_readability['feats'][feat]
            })    
    
    return [
      {'aspect': 'general', 'data': count_features },
      {'aspect': 'readability', 'data': readability_features },
    ]

def get_features_helper_on_tagging(content, lang, level, removed_features=[], overview=False):
            
    ###Lexical feature extraction
    if overview:
        content_lexical_scalars = vars(Lexical_features(content, lang=lang, level=level))
    else:
        content_lexical_scalars = eval_str(content.lexical)
    
    if level != 'sent':
        if overview:
            content_lexical_average = vars(Lexical_features(content, lang=lang, algorithm="average", level=level))
        else:
            content_lexical_average = eval_str(content.lexical_average)
    
    lexical_features = []
    
    for feat in [key for key in content_lexical_scalars['feats'].keys() if '$' not in key]:
        if feat in removed_features:
            continue
        if level != 'sent':
            lexical_features.append({
              'name':feat, 'scalar':content_lexical_scalars['feats'][feat], \
              'mean':content_lexical_average['feats'][feat]['mean'], \
              'median':content_lexical_average['feats'][feat]['median']
            })
        else:
            lexical_features.append({
              'name':feat, 'scalar':content_lexical_scalars['feats'][feat]
            })
    
    ### morph feature extraction
    # 
    # 
    if overview:
        scalar_dict = vars(Morph_features(content, lang=lang, level=level))
    else:
        scalar_dict = eval_str(content.morph)
    dict2index = { name:index for index, name in enumerate([c['name'] for c in scalar_dict['feats']])}
    if level !='sent': 
        if overview:
            content_morph_average = Morph_features(content, lang=lang, algorithm="average", level=level)
            average_dict = vars(content_morph_average)
        else:
            average_dict = eval_str(content.morph_average)

    #six categories
    categories =  \
    """
    VERBFORM,PoS-PoS,SubPoS-ALL, PoS-ALL, PoS-MultiPoS, MultiPoS-MultiPoS

    """.split(',')
    

    morph_features = []
    for c in categories:
        cc = c.strip().lstrip()
        #cc = c.lower().replace('-','_')
        morph_features.append(OrderedDict({'name':cc, 'children':[]}))
        for feat in [key for key in scalar_dict['feats'][dict2index[cc]]['data'].keys() if '$' not in key]:
        #for feat in average_dict[cc].keys():
            if feat in removed_features:
                continue
            if level != 'sent':
                morph_features[-1]['children'].append({'name':feat, 'scalar':scalar_dict['feats'][dict2index[cc]]['data'][feat], \
                                                'mean': average_dict['feats'][dict2index[cc]]['data'][feat]['mean'], \
                                                'median': average_dict['feats'][dict2index[cc]]['data'][feat]['median']})
            else:
                morph_features[-1]['children'].append({'name':feat, 'scalar':scalar_dict['feats'][dict2index[cc]]['data'][feat]})
        
    ###syntactic feature extraction
    if overview:
        content_syntactic_scalars = vars(Syntactic_features(content, level=level))
    else:
        content_syntactic_scalars = eval_str(content.syntactic)
    if level != 'sent':
        if overview:
            content_syntactic_average = vars(Syntactic_features(content, algorithm="average", level=level))
        else:
            content_syntactic_average = eval_str(content.syntactic_average)
    
    syntactic_features = []
    for feat in [key for key in content_syntactic_scalars['feats'].keys() if '$' not in key]:
        if feat in removed_features:
            continue
        if level != 'sent':
            syntactic_features.append({
              'name':feat, 'scalar':content_syntactic_scalars['feats'][feat], \
              'mean':content_syntactic_average['feats'][feat]['mean'], \
              'median':content_syntactic_average['feats'][feat]['median']
            })
        else:
            syntactic_features.append({
              'name':feat, 'scalar':content_syntactic_scalars['feats'][feat]
            })  
    
    return [
      {'aspect': 'lexical', 'data': lexical_features},
      {'aspect': 'morph', 'data': morph_features},
      {'aspect': 'syntactic', 'data': syntactic_features}
    ]
    
def get_feature_helper(content, lang, level, removed_features=[], tokenization_only=False, tagging_only=False, overview=False):
    
    if tokenization_only:
        return get_features_helper_on_tokenization(content, lang, level, removed_features, overview)
    elif tagging_only:
        return get_features_helper_on_tagging(content, lang, level, removed_features, overview)
    else:
        general, readability = get_features_helper_on_tokenization(content, lang, level, removed_features, overview)
        lexical, morph, syntactic = get_features_helper_on_tagging(content, lang, level, removed_features, overview)
        return [ general, readability, lexical, morph, syntactic ]

"""
The classes AllSentences and AllParagraphs are temporary data 
used for merging sentences, paragraphs respective texts given the selected texts
in order to computate statistics.
"""
class AllSentences:
    def __init__(self, sentences=[]):
        self.sentences = sentences
        self.general = None
        

class AllParagraphs:
    def __init__(self, paragraphs=[], sentences=[]):
        self.paragraphs = paragraphs
        self.sentences = sentences # [sent for paragraph in self.paragraphs for sent in paragraph.sentences()]
        self.general = None


class TextElement(AllParagraphs):
    def __init__(self, text, paragraphs=[], sentences=[]):
        super(TextElement, self).__init__(paragraphs, sentences)
        t = Text.objects.get(stats=text)
        self.general = eval_str(t.general)
        self.readability = eval_str(t.readability)
        self.lexical = eval_str(t.lexical)
        self.lexical_average = eval_str(t.lexical_average)
        self.morph = eval_str(t.morph)
        self.morph_average = eval_str(t.morph_average)
        self.syntactic = eval_str(t.syntactic)
        self.syntactic_average = eval_str(t.syntactic_average)

class Texts:
    def __init__(self, texts):
        self.texts = texts
        self.general = None
        self.index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == len(self.texts):
            self.index = 0  # restart index when looping is over
            raise StopIteration
        self.index = self.index + 1
        return self.texts[self.index-1]



        
def assgin_chosen_text_info_by_category(text, data, annotation_type):
    def add(is_included):
        if is_included:
            data['valid_texts'].append([text.id, text.filename])
            data['number_of_valid_texts'] += 1
        else:
            data['invalid_texts'].append([text.id, text.filename])
        return data

    if annotation_type == 'normalized':
        return add(text.normalized)
    elif annotation_type == 'parsed': 
        return add(text.parsed)
    return add(True)
            

def initialize_texts_info():

    return {
      'number_of_valid_texts': 0,
      'valid_texts': [],
      'invalid_texts': []
    }

def get_chosen_texts_info(request, *args, **kwargs):
    
    annotation_types = ['tokenized', 'normalized', 'parsed']
    data = {
      category: initialize_texts_info() for category in annotation_types
    }
    # text2settings = {}
    data = {
      **data,
      'total_sent_items': 0,
      'total_para_items': 0,
      'total_text_items': 0,
    }
    text_list = get_text_list(request)
    # text_list = get_text_list(request, lang)

    # for text in text_list:
    #     text2settings[str(text.text_id)] = {
    #       'normalized': text.normalized,
    #       'parsed': text.parsed, 
    #     }

    for annotation_type in annotation_types:
        for text in text_list:

            data[annotation_type] = assgin_chosen_text_info_by_category(text, data[annotation_type], annotation_type)
    
    text_list = [ text for text in text_list if text.parsed ]
    
    
    if text_list:
        data['total_text_items'] = len(text_list)
        data['total_para_items'] = sum([t.number_of_paragraphs for t in text_list])
        data['total_sent_items'] = sum([t.number_of_sentences for t in text_list])

    return JsonResponse(data)

def get_tagged_and_untagged_texts(text_list):

    tagged_texts, untagged_texts = [], []

    for text in text_list:
        if text.parsed:
            tagged_texts.append(text)
        else:
            untagged_texts.append(text)
    return tagged_texts, untagged_texts

def get_overview_features(text_list, lang, level, removed_features=[], *args, **kwargs):

    tagged_texts, untagged_texts = get_tagged_and_untagged_texts(text_list)

    if level == 'sent':
        next_level = 'para'
    elif level == 'para':
        next_level = 'text'
    elif level == 'text':
        next_level = 'texts'

    if untagged_texts:
        content_tokenized = generate_content(text_list, level)
        general, readability = get_features_helper_on_tokenization(content_tokenized, lang, next_level, removed_features, overview=True)    
        features = [general, readability]
        if tagged_texts:
            content_tagged = generate_content(tagged_texts, level)
            lexical, morph, syntactic = get_features_helper_on_tagging(content_tagged, lang, next_level, removed_features, overview=True)
            features = [ general, readability, lexical, morph, syntactic ]
                   
    else:
        content = generate_content(text_list, level)
        features = get_feature_helper(content, lang, next_level, removed_features, overview=True)
    
    return {'data': features}


def fetch_overview_features(request, level, *args, **kwargs):
    text_list = get_text_list(request)
    lang = json.loads(request.body)['lang']
    data = get_overview_features(text_list, lang, level)
    
    return JsonResponse(data, safe=False)


def get_detail_features_helper(lang, level, text, removed_features, features, tagged=False):
    text_instance = Text.objects.get(stats=text)
    if level == 'sent':
        content = Sentence.objects.all().filter(text=text_instance)
    elif level == 'para':
        content = Paragraph.objects.all().filter(text=text_instance)
    else:
        content = [text_instance]

    for element in content:
        if tagged:
            feats = get_feature_helper(element, lang, level, removed_features)
        else:
            feats = get_features_helper_on_tokenization(element, lang, level, removed_features)
        features.append({
          'text': text.filename,
          'content': str(element),
          'data': feats
        })
    return features
       

def get_detail_features(text_list, lang, level, removed_features, *args, **kwargs):

    tagged_texts, untagged_texts = get_tagged_and_untagged_texts(text_list)

    if untagged_texts:
        for text in untagged_texts:
            features = get_detail_features_helper(lang, level, text, removed_features, features=[])
    if tagged_texts:
        for text in tagged_texts:
            features = get_detail_features_helper(lang, level, text, removed_features, features=[], tagged=True)
    
    return features        
  
                
#def get_general_features_for_all_texts(request, lang, level, *args, **kwargs):

def generate_content(text_list, level, *args, **kwargs):

    if level == 'sent':
        return AllSentences(
          sentences = [ s for text in text_list \
                          for s in Sentence.objects.filter(
                            text=Text.objects.get(stats=text)
                          )
                      ]
        )
    
    if level == 'para':
        return AllParagraphs(
          paragraphs = [ p for text in text_list \
                          for p in Paragraph.objects.filter(
                            text=Text.objects.get(stats=text)
                          )
                      ],
          sentences = [ s for text in text_list \
                          for s in Sentence.objects.filter(
                            text=Text.objects.get(stats=text)
                          )
                      ]
        )
    if level == 'text':
        # return [ Text.objects.get(stats=text) for text in text_list ]
        return Texts( texts=[
          TextElement(
            text,
            paragraphs = Paragraph.objects.filter(
              text=Text.objects.get(stats=text)
            ),
            sentences = Sentence.objects.filter(
              text=Text.objects.get(stats=text)
            )
          ) for text in text_list
          ]
        )
   


def get_content_by_level(text_list, level, start, size):
    """
    text list is a list of instances of TextStats
    start, end refer to indeces
    """
    content = []
    def assert_level_error():
        print('LEVEL ERROR: Invalid level: %s' % level)
        assert False
    for text in text_list:
        if level == 'sentence':
            number = text.number_of_sentences
        elif level == 'paragraph':
            number = text.number_of_paragraphs
        else:
            assert_level_error()
        if number <= start:
            start -= number
            continue

        text_instance = Text.objects.get(stats=text)
        if level == 'sentence':
            conts = Sentence.objects.filter(text=text_instance).order_by('id')
        elif level == 'paragraph':
            conts = Paragraph.objects.filter(text=text_instance).order_by('id')
        else:
            assert_level_error()
        content.extend(conts[start: start+size])
        if len(content) < size:
            start = 0
            size -= len(conts[start: start+size])
        else:
            return content
    return content

def get_features(request, level, page, **kwargs):
    """
    level: texts, text <text-id>, paragraph <text-id, paragraph-id>, sentence <text-id, paragraph-id, sentence-id>
    aspect: general, readability, lexcial, morphological, syntactic, all_features
    This function works with pagination
    
    The default page size is 10; page size is supposed to be defined in config.py
    """

    text_list = get_text_list(request)
    lang = json.loads(request.body)['lang']
    data = {'content':[], 'statistics':[]}
    data['number_of_texts'] = len(text_list)
    start = int(page) * PAGE_SIZE - PAGE_SIZE
    if text_list:
        if level == 'text':
            content = [ Text.objects.get(stats=text) for text in text_list[start:start+PAGE_SIZE] ]
        elif level == 'para':
            content = get_content_by_level(text_list, 'paragraph', start, PAGE_SIZE)
        elif level == 'sent':
            content = get_content_by_level(text_list, 'sentence', start, PAGE_SIZE)
        else:
            return JsonResponse({'error':'level %s is invalid' % level})
        
        # js can not handle breakline shown in python
        # if level != 'text':
        data['content'] = [str(e) for e in content]
        for index, cont in enumerate(content, start):
            if level == 'text':
                tokenized_only = not cont.stats.parsed
            else:
                tokenized_only = not cont.text.stats.parsed
            data['statistics'].append(
              {
                'id': index, 
                'data': get_feature_helper(cont, lang, level, tokenization_only=tokenized_only)
              }
            )         
    return JsonResponse(data, safe=False)


def get_freq_list(texts, category, tagset):
    if category.lower() != 'norm':
        return merge_defaultdicts([
            eval_str(Text.objects.get(stats=text).general)[
            'freq_%s_dict_%s' % (category, tagset)
            ] for text in texts
        ])
    return merge_defaultdicts(
      [
        eval_str(Text.objects.get(stats=text).general)[
          'freq_%s_dict_%s' % (category, tagset)
        ] for text in texts if text.normalized is not False
      ]
    )

def extend_unknown_pos_token(category, base_list, added_text_list, include_punct):
    unknown_pos_token_count = dict()
    for t in added_text_list:
        text = Text.objects.get(stats=TextStats.objects.get(text_id=t.text_id))
        for token, count in eval_str(text.general)['freq_%s_dict_upos' % category.lower()].items():
            try:
                key = token.split('__')[0]
                if include_punct is False and key in string.punctuation:
                    continue
                if key not in unknown_pos_token_count:
                    unknown_pos_token_count[key] = {
                      'count': count,
                      'pos': 'Unknown',
                      category: key,
                      'length': len(key)
                    }
                else: 
                    unknown_pos_token_count[key]['count'] += count
            except Exception:
                pass
    # print(unknown_pos_token_count.values())
    base_list.extend(list(unknown_pos_token_count.values()))
    return base_list


def get_type(request, category, tagset, **kwargs):
    """
    implement the API for computing the counts of 
    form, norm or lemma
    obs: punctuation is not included in the length computation
    return {
        form_pos: {},
        pos_list: [],
        texts_not_normalized: [text_id],
        texts_not_parsed: [text_id]
    }
    """
    lang = json.loads(request.body)['lang']
    check_length = json.loads(request.body).get('length', False)
    text_list = get_text_list(request, category=category)
    data = {
      'number_of_texts': len(text_list)
    }

    if category != 'lemma':
        tagged_text_list, untagged_text_list = [], []
        normalized_untagged_text_list = []
        for text in text_list:
            if text.parsed:
                tagged_text_list.append(text)
            else:
                untagged_text_list.append(text)
                if category == 'norm' and text.normalized:
                    normalized_untagged_text_list.append(text)
            
        dicts = get_freq_list(tagged_text_list, category, tagset)
    
    else:
        dicts = get_freq_list(text_list, category, tagset)
                  
    cate_pos_token_list = [
      {
        'count':value, 
        'pos':key.split('_')[-1], 
        category:'_'.join(key.split('_')[:-1])
      } for key, value in sorted(list(dicts.items()), key=lambda x:x[1], reverse=True)
    ]

    if check_length: # when calculating length
        # example [{'count': 17, 'pos': 'ADP', 'form': 'i', 'length': 1}]
        if tagset == 'upos':
            cate_pos_token_list = [{**e, 'length':len(e[category])} for e in cate_pos_token_list if e['pos'] != 'PUNCT']
        elif tagset == 'xpos' and lang == 'sv':
            cate_pos_token_list = [{**e, 'length':len(e[category])} for e in cate_pos_token_list if e['pos'] not in SUC_TAGS[-3:]]
        elif tagset == 'xpos' and lang == 'en':
            cate_pos_token_list = [{**e, 'length':len(e[category])} for e in cate_pos_token_list if e['pos'] not in PT_TAGS[-10:]]

        if category == 'norm':
            if normalized_untagged_text_list:
                cate_pos_token_list = extend_unknown_pos_token(category, cate_pos_token_list, normalized_untagged_text_list, False)
        elif category == 'form':
            if untagged_text_list:
                cate_pos_token_list = extend_unknown_pos_token(category, cate_pos_token_list, untagged_text_list, False)
    else:
        if category == 'norm':
            if normalized_untagged_text_list:
                cate_pos_token_list = extend_unknown_pos_token(category, cate_pos_token_list, normalized_untagged_text_list, True)
        elif category == 'form':
            if untagged_text_list:
                cate_pos_token_list = extend_unknown_pos_token(category, cate_pos_token_list, untagged_text_list, True)
            
    
    pos_dict = {}
    for e in cate_pos_token_list:
        if e['pos'] in pos_dict:
            pos_dict[e['pos']] += e['count']
        else:
            pos_dict[e['pos']] = e['count']

    pos_list = sorted(pos_dict.items(), key=lambda x:x[1], reverse=True)

    if not check_length:
        data['pos_list'] = pos_list
        data['%s_pos' % (category)] = cate_pos_token_list
    else:
        length_dict = {}
        """
        length_dict {
          1: {
            pos:{
              PP: {
                i:Number
              }
            }
          }
        }
        """
        for e in cate_pos_token_list:
            if e['length'] in length_dict:
                if e['pos'] in length_dict[e['length']]:
                    if e[category] in length_dict[e['length']][e['pos']]:
                        length_dict[e['length']][e['pos']][e[category]] += e['count']
                    else:
                        length_dict[e['length']][e['pos']][e[category]] = e['count']
                else:
                    length_dict[e['length']][e['pos']] = {e[category]:e['count']}
            else:
                length_dict[e['length']] = {e['pos']:{e[category]:e['count']}}
        pos_list = [e for e, _ in pos_list]

        def serialize_pos(d):
            r = {'total':0, 'data':[]}
            if d:
                r['total'] = sum(d.values())
                r['data'] = [{'type':key, 'count':value} for key, value in d.items()]
            return r
        length_list = [{
          'Length':{'total':length, 
            'data':[{'type':pos, 'count': sum(length_dict[length][pos].values())} for pos in length_dict[length].keys()]
            },
          **{
            pos:serialize_pos(length_dict[length].get(pos, {})) for pos in pos_list
          },
        } for length in sorted(length_dict.keys())]

        # add total for each length
        length_list = [{
          **length, 
          'Total':{
            'total':sum([d['count'] for d in length['Length']['data']]),
            'data':[]
          }} for length in length_list]
        # this works as a table head  e.g. [{ label: 'NN', prop: 'NN' }]
        pos_list = [{'label':pos, 'prop':pos} for pos in ['Length'] + pos_list + ['Total']]
        data['pos_list'] = pos_list
        data['length_list'] = length_list
    return JsonResponse(data)
