#!/usr/bin/env python3
# encoding: utf-8

# The list of lexical features:
"""
Avg KEELY log freq
A1 lemma INCSC
A2 lemma incsc
B1 lemma incsc
B2 lemma incsc
C1 lemma incsc
C2 lemma incsc
difficult word incsc
difficult noun & verb incsc
oov incsc 
no lemma incsc
""" 

import math
import json
from collections import Counter
from .statistics import mean, median
from .helpers import eval_str
import os
from collections import OrderedDict
import codecs

#########################################################################
############specific lexical feature computation#########################
#########################################################################

def lemma_incsc(sentence, cefr, kelly_dict, raw=True): # typ is which cefr level the sentence is involved, d is dict
    """
    cefr is 1,2,3,4,5,6 which represents A1, A2, B1, B2, C1, C2
    this function will be applied to extra the values of the following features
    A1 lemma INCSC
    A2 lemma INCSC
    B1 lemma INCSC
    B2 lemma INCSC
    C1 lemma INCSC
    C2 lemma INCSC
    #Missing lemma form INCSC
    #Out-of Kelly-list INCSC
    """
    t = len(sentence.tokens)
    sent_cefr = []
    for token in sentence.tokens:
        if token.lemma+'|'+token.upos in kelly_dict:
            sent_cefr.append(kelly_dict[token.lemma+'|'+token.upos])
        else:
            sent_cefr.append(None)
    countDict = {t:counts for t,counts in Counter(sent_cefr).most_common()}
    if raw:
        return countDict.setdefault(cefr, 0), t
    return float(countDict.setdefault(cefr,0))/t

def difficult_word(sentence, kelly_dict,noun_verb=False, raw=True):
    # difficult words refer to words above and inclunding B1 level

    t,p = len(sentence.tokens), 0
    for token in sentence.tokens:
        if token.lemma+'|'+token.upos in kelly_dict:
            if kelly_dict[token.lemma+'|'+token.upos] in "3456":
                if noun_verb:
                    if token.upos in ["NOUN","VERB"]: #Only noun and verb valid, not propn and aux
                        p += 1
                        continue
                else:
                    p += 1
    if raw:
        return p, t
    return float(p*1000)/t

def out_of_kelly(sentence, kelly_dict, raw=True):
    if not sentence:
        return 0.0
    t,p = len(sentence.tokens), 0
    for token in sentence.tokens:
        if token.lemma+"|"+token.upos not in kelly_dict:
            p += 1
    if raw:
        return p, t
    return float(p*1000)/t

def kelly_log_frequency(sentence, wpm_dict, wpms=[], raw=True):
    """
    WPM is used to compute the avg kelly log freq
    the computation of log-freq for the tokens out of the kelly list is ignored
    the natural logarthigm is used
    """
    if not sentence:
        return [] if raw else 0.0
    
    if not wpms:
        wpms = [wpm_dict[token.lemma+'|'+token.upos] for token in sentence.tokens if token.lemma+'|'+token.upos in wpm_dict]
  
    return wpms if raw else mean([math.log(wpm) for wpm in wpms])

#########################################################################
############lexical feature computation##################################
#sentence_level##############text_level##################################
#########################################################################
class Lexical_features:

    def __init__(self, content, lang, algorithm='', level='sent'):

        #load the dict according to the lang:
        PIPE_DIR = os.path.realpath(__file__).replace(os.path.basename(os.path.realpath(__file__)), '')
        NLP_DIR = os.path.join(PIPE_DIR, 'pipeline', 'nlp')

        if lang =='sv':
            kelly_dict_path = os.path.join(NLP_DIR, 'sv_kelly_cefr')
            wpm_dict_path = os.path.join(NLP_DIR, 'sv_kelly_wpm')
            with codecs.open(wpm_dict_path, 'r', 'utf-8') as f:
                wpm_dict = json.load(f)
        elif lang == 'en':
            kelly_dict_path = os.path.join(NLP_DIR, 'en_kelly_cefr') 
            #wpm_dict_path = os.path.join(NLP_DIR, 'sv_kelly_wpm')    ###en_kelly_wpm is not found; we exclude the feature of out of kelly-log frequency features
        with codecs.open(kelly_dict_path, 'r', 'utf-8') as f:
            kelly_dict = json.load(f)
                
        functions = [
            ('A1 lemma INCSC', lemma_incsc, {'cefr':'1', 'kelly_dict':kelly_dict}),
            ('A2 lemma INCSC', lemma_incsc, {'cefr':'2', 'kelly_dict':kelly_dict}),
            ('B1 lemma INCSC', lemma_incsc, {'cefr':'3', 'kelly_dict':kelly_dict}),
            ('B2 lemma INCSC', lemma_incsc, {'cefr':'4', 'kelly_dict':kelly_dict}),
            ('C1 lemma INCSC', lemma_incsc, {'cefr':'5', 'kelly_dict':kelly_dict}),
            ('C2 lemma INCSC', lemma_incsc, {'cefr':'6', 'kelly_dict':kelly_dict}),
            ('Difficult Word INCSC', difficult_word, {'kelly_dict':kelly_dict}),
            ('Difficult Noun or Verb INCSC', difficult_word, {'kelly_dict':kelly_dict, 'noun_verb':True}),
            ('Out of Kelly-list INCSC',out_of_kelly, {'kelly_dict':kelly_dict})
        ]

        if lang == 'sv':
            functions.append(('Kelly log-frequency', kelly_log_frequency, {'wpm_dict':wpm_dict}))

        self.feats = OrderedDict()
        self.sent_raw = OrderedDict()
        
        if algorithm == '':
            for name, func, kwarg in functions:
                if name == 'Kelly log-frequency':
                    if level == 'sent':
                        wpms = func(content, **kwarg)
                        self.feats['$'.join([name, 'raw'])] = wpms
                        kwarg['raw'] = False
                        kwarg['wpms'] = wpms
                        self.feats[name] = func(content, **kwarg)
                    elif level in ['text', 'para']:
                        wpms, wpms_scalars = list(), list()
                        for sent in content.sentences:
                            wpms.extend(eval_str(sent.lexical)['feats']['$'.join([name, 'raw'])])
                            wpms_scalars.append(eval_str(sent.lexical)['feats'][name])
                        self.sent_raw[name] = wpms_scalars
                        self.feats[name] = mean(wpms_scalars)
                        self.feats['$'.join([name, 'raw'])] = wpms
                    elif level == 'texts':
                        wpms_scalars = list()
                        for text in content:
                            wpms_scalars.append(eval_str(text.lexical)['feats'][name])
                        self.feats[name] = mean(wpms_scalars)
                    continue
                
                if level == 'sent':
                    c, t = func(content, **kwarg)
                         
                elif level in ['para', 'text']:
                    c, t, sent_scalars = 0, 0, []
                    for sent in content.sentences:
                        sc, st = eval_str(sent.lexical)['feats']['$'.join([name, 'raw'])]
                        c += sc
                        t += st
                        sent_scalars.append(eval_str(sent.lexical)['feats'][name])
                    self.sent_raw[name] = sent_scalars

                elif level == 'texts':
                    c, t = 0, 0 
                    for text in content:
                        sc, st = eval_str(text.lexical)['feats']['$'.join([name, 'raw'])]
                        c += sc
                        t += st
                scalar = round(c/t*1000, 2) if t else 1000 #set 1000 as the ceiling
                self.feats[name] = scalar
                self.feats['$'.join([name, 'raw'])] = c, t
            
        elif algorithm == 'average':
            for name, _, _ in functions:
                values = []                    
                
                if level != 'texts':
                    for sentence in content.sentences:
                        values.append(eval_str(sentence.lexical)['feats'][name])
                    self.feats[name] = {'mean':mean(values), 'median':median(values)}
                else:
                    for text in content:
                        values.extend(eval_str(text.lexical)['sent_raw'][name])
                    self.feats[name] = {'mean':mean(values), 'median':median(values)}
           
