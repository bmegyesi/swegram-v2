#!/usr/bin/env/ python3
#encoding: utf-8
from .statistics import mean, median
from collections import OrderedDict
from .helpers import eval_str

#This script is to collect morphological features

"""
subgroup 1
1 	 Modal VERB to VERB
2    S-VERB to VERB (swedish only)
3    Present Participle to VERB
4    Past Participle to VERB
5    Present VERB to VERB
6    Past VERB to VERB
7    Supine VERB to VERB
subgroup 2
1    ADJ INCSC
2    ADV INCSC
3    NOUN INCSC
4    PART INCSC
5    PUNCT INCSC
6    SCONJ INCSC
7    VERB INCSC
subgroup 3
1    NOUN to VERB
2    PRON to NOUN
3    PRON to PREP
subgroup 4
1    ADJ Variation
2    ADV Variation
3    NOUN Variation
4    VERB Variation
subgroup 5
1    CCONJ & SCONJ INCSC
2    Functional Token INCSC
3    Lex to Non-Lex
4    Lex to Token
5    Nominal Ratio
6    Rel INCSC
subgroup 6
1    Neuter Gender NOUN INCSC (only for swedish)
2    3SG PRON INCSC (only for english)
3    S-VERB INCSC  (only for swedish)
"""

########################Functions to extract morphological features######################
def verbs_to_verbs(sentence,verb_type, raw=True):
    """this can be applied to   modal verbs to verbs
                                past participles to verbs
                                present verbs to verbs
                                supine verbs to verbs

    The verb type can be
                            Swedish English
                            AUX                             modal(but not vara, ha) ? bli komma
                                        MD                  modal
                            VB|PRS      VBP, VBZ            present
                            VB|PRT      VBD                 past
                            VB|SUP                          supine (only for swedish)
                            Past_part   VBN                 past participles
                            Pres_part   VBG                 present participles

    english has the following pos for verbs
    vb  VerbForm=Fin:/
    vbn Tense=Past|VerbForm=Part
    vbd Tense=Past|VerbForm=Fin
    vbg Tense=Pres|VerbForm=Part or VerbForm=Ger gerund
    vbp Tense=Pres|VerbForm=Fin
    vbz Tense=Pres|VerbForm=Fin
    """

    verb, verbs = 0,0
    if verb_type == "AUX":
        for token in sentence.tokens:
            if token.upos == "AUX": # and token.norm not in ["vara","ha"]:
                verb += 1
                verbs += 1
            elif token.upos in ["VERB","AUX"]:
                verbs += 1
    else:
        for token in sentence.tokens:
            if verb_type == "Pres_part":
                if "VerbForm=Part" in token.feats and "Tense=Pres" in token.feats:
                    verb += 1
            elif verb_type == "Past_part":
                if "VerbForm=Part" in token.feats and "Tense=Past" in token.feats:
                    verb += 1
            elif verb_type in token.xpos:
                    verb += 1
            if token.upos in ["VERB","AUX"]:
                verbs += 1
    if raw:
        return verb, verbs
    if not verbs:
        return 0.0 #needs to be modified
    return float(1000 * verb) / verbs


def pos_incsc(sentence,pos,variation=False, raw=True):
    """This function can be applied to compute for shared specific morphological
     feature in Swedish and English. These parts of speech include
     particle, punctuation, subjunction, adjective, adverb, noun, verb.
     If variation is set to be True, the base is changed from all parts of speech
     into content parts of speech: noun, verb, adverb, adjective

     """
    if not sentence:
        return 0.0
    if variation:
        t = 0
        for token in sentence.tokens:
            if token.upos in ["NOUN","ADJ","ADV","VERB"]: #propn is not included as lexical category
                t += 1
    else:
        t = len(sentence.tokens)
    p = 0
    for token in sentence.tokens:
        if token.upos == pos:
            p += 1
    if raw:
        return p, t
    if not t:
        return 0.0
    return float(1000 * p) / t


def function_tokens_incsc(sentence, lex=False, lex_to_non_lex=False, raw=True):
    if not sentence:
        return 0.0
    t = len(sentence.tokens)
    p = 0

    for token in sentence.tokens:
        if token.upos not in ["NOUN","ADJ","ADV","VERB","PROPN","INTJ"]:#a set of open class words
            p += 1 # p is count for non-lexical tokens
    if raw:
        if lex:
            return p, t
        elif lex_to_non_lex:
            return p, t-p
        else:
            return t-p, t
    if lex:
        return 1000 * (1 - float(p)/t )
    elif lex_to_non_lex and p:
        return 1000 * (float(t-p)/p)
    elif lex_to_non_lex:
        return 0.0 #(needs to be modified here)
    return float(1000 * p) / t


def con_subj_incsc(sentence, raw=True):
    if not sentence:
        return 0.0
    t = len(sentence.tokens)
    p = 0

    for token in sentence.tokens:
        if token.upos in ["CCONJ","SCONJ"]:
            p += 1
    if raw:
        return p,t
    return float(1000 * p) / t


def pos_pos_ratio(sentence, pos1, pos2, raw=True): # this is a ratio, not a incsc score
    """This can be applied for the ratio between two parts of speech
     They can be    pronouns to nouns
                    pronouns to prepositions
                    nouns to verbs
    """
    if not sentence:
        return 0.0
    p1,p2 = 0,0
    for token in sentence.tokens:
        if token.upos == pos1:
            p1 += 1
        elif token.upos == pos2:
            p2 += 1
    if raw:
        return p1, p2
    if not p1 or not p2:
        return 0.0
    return float(p1) / p2 * 1000


def thirdSG_pronoun_incsc(sentence, raw=True): #only for english
    if not sentence:
        return 0.0
    p = 0
    t = len(sentence.tokens)
    for token in sentence.tokens:
        if "Number=Sing" in token.feats and token.upos == "PRON" and token.lemma not in 'jag vi du ni':
            p += 1
    if raw:
        return p,t
    return float(1000 * p) / t


def neuter_gender_noun_incsc(sentence, raw=True): #only for swedish
    if not sentence:
        return 0.0
    p = 0
    t = len(sentence.tokens)
    for token in sentence.tokens:
        if token.upos == "NOUN" and "Gender=Neut" in token.feats:
            p += 1
    if raw:
        return p, t
    return float(1000 * p) / t


def s_verbs_incsc(sentence,verb=False, raw=True):
    """three types
    reciprocal verbs
    passive verbs
    deponent
    AUX is not considered here
    """

    if not sentence:
        return 0.0
    p = 0
    if not verb:
        t = len(sentence.tokens)
    else:
        t = 0
    for token in sentence.tokens:
        if token.upos == "VERB" and verb:
            t += 1
        if token.form[-1] == "s" and token.upos == "VERB":
            p += 1
    if raw:
        return p,t
    return float(1000 * p) / t


def relative_structure_incsc(sentence,raw=True):
    """
    (HA + HD + HP + HS) / (ALL pos tags)
    HA Interrogative/Relative Adverb)
    HD Interrogative/Relative Determiner
    HP Interrogative/Relative Pronoun
    HS Interrogative/Relative Possessive
    """

    if not sentence:
        return 0.0
    p, t = 0, len(sentence.tokens)

    for token in sentence.tokens:
        """Int: interrogative; Rel: Relative"""
        if "PronType=Int" in token.feats or "PronType=Rel" in token.feats:
            p += 1
    if raw:
        return p, t
    return float(1000*p) / t


def nominal_ratio(sentence,raw=True):
    
    """
    simple: nn/vb
    full: (nn+pp+pc) / (pn+ab+vb) 
    """ # pc is participle
    if not sentence:
        return 0.0
    p, t = 0, 0

    for token in sentence.tokens:
        if token.xpos.split("|")[0] in ["NN","PP","PC"]:
            p += 1
        if token.xpos.split("|")[0] in ["PN","AB","VB"]:
            t += 1
    if raw:
        return p, t
    if not t:
        return 0.0
    return float(p)/t * 1000 
    

class Morph_features:
    """function item: name, function, param, params"""
    
    functions = {
        'VERBFORM':[
            ('Modal VERB to VERB', verbs_to_verbs, {'verb_type':'AUX'}),
            ('Present Participle to VERB', verbs_to_verbs, {'verb_type':'Pres_part'}),
            ('Past Participle to VERB', verbs_to_verbs, {'verb_type':'Past_part'}),
            ('Present VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRS'}),
            ('Past VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRT'}),
            ('Supine VERB to VERB', verbs_to_verbs, {'verb_type':'VB|SUP'}),
            ('S-VERB to VERB', s_verbs_incsc, {"verb":True}) #Swedish only
        ], 
        'PoS-ALL':[
            ('ADJ INCSC', pos_incsc, {"pos":"ADJ", "variation":False}),
            ('ADV INCSC', pos_incsc, {"pos":"ADV", "variation":False}),
            ('NOUN INCSC', pos_incsc, {"pos":"NOUN", "variation":False}),
            ('PART INCSC', pos_incsc, {"pos":"PART", "variation":False}),
            ('PUNCT INCSC', pos_incsc, {"pos":"PUNCT", "variation":False}),
            ('SCONJ INCSC', pos_incsc, {"pos":"SCONJ", "variation":False}),
            ('VERB INCSC', pos_incsc, {"pos":"VERB", "variation":False})
        ],
        'PoS-PoS':[
            ('NOUN to VERB', pos_pos_ratio, {"pos1":"NOUN", "pos2":"VERB"}),
            ('PRON to NOUN', pos_pos_ratio, {"pos1":"PRON", "pos2":"NOUN"}),
            ('PRON to PREP', pos_pos_ratio, {"pos1":"PRON", "pos2":"PREP"})
        ],
        'PoS-MultiPoS':[
            ('ADJ Variation', pos_incsc, {"pos":"ADJ", "variation":True}),
            ('ADV Variation', pos_incsc, {"pos":"ADV", "variation":True}),
            ('NOUN Variation', pos_incsc, {"pos":"NOUN", "variation":True}),
            ('VERB Variation', pos_incsc, {"pos":"VERB", "variation":True})
        ],
        'MultiPoS-MultiPoS':[
            ('CCONJ & SCONJ INCSC', con_subj_incsc, {}),
            ('Functional Token INCSC', function_tokens_incsc, {}),
            ('Lex to Non-Lex', function_tokens_incsc, {'lex_to_non_lex':True}),
            ('Lex to Token', function_tokens_incsc, {'lex':True}),
            ('Nominal Ratio', nominal_ratio, {}),
            ('Rel INCSC', relative_structure_incsc, {})
        ],
        'SubPoS-ALL':[
            ('S-VERB INCSC', s_verbs_incsc, {}),                        #swedish only
            ('Neuter Gender NOUN INCSC', neuter_gender_noun_incsc, {}), #swedish only
            ('S-VERB INCSC', thirdSG_pronoun_incsc, {})                 #english only 
        ]     
    }
    dict2index = {name:index for index, name in enumerate([
        'VERBFORM','PoS-PoS', 'SubPoS-ALL', 'PoS-ALL', 'PoS-MultiPoS', 'MultiPoS-MultiPoS'
    ])}

    """
    features = {
        'VERBFORM': \
            ['Modal VERB to VERB', 'Present Participle to VERB', 'Past Participle to VERB', \
             'Present VERB to VERB', 'Past VERB to VERB', 'Supine VERB to VERB', 'S-VERB to VERB'], 
        'PoS_PoS': ['NOUN to VERB', 'PRON to NOUN', 'PRON to PREP'], 
        'SubPoS_ALL': ['S-VERB INCSC', 'Neuter Gender NOUN INCSC', 'S-VERB INCSC'], 
        'PoS_ALL': ['ADJ INCSC', 'ADV INCSC', 'NOUN INCSC', 'PART INCSC', 'PUNCT INCSC', 'SCONJ INCSC', 'VERB INCSC'], 
        'PoS_MultiPoS': ['ADJ Variation', 'ADV Variation', 'NOUN Variation', 'VERB Variation'], 
        'MultiPoS_MultiPoS': \
            ['CCONJ & SCONJ INCSC', 'Functional Token INCSC', \
            'Lex to Non-Lex', 'Lex to Token', 'Nominal Ratio', 'Rel INCSC']
    }
    """

    #features = {sub:[f[0] for f in functions[sub]] for sub in ['VERBFORM', 'PoS-PoS', 'SubPoS-ALL', 'PoS-ALL', 'PoS-MultiPoS', 'MultiPoS-MultiPoS']}

    def __init__(self, content, lang, algorithm='', level='sent'):
        self.feats = [
            OrderedDict({'name':'VERBFORM','data':OrderedDict()}),
            OrderedDict({'name':'PoS-PoS', 'data':OrderedDict()}),
            OrderedDict({'name':'SubPoS-ALL', 'data':OrderedDict()}),
            OrderedDict({'name':'PoS-ALL', 'data':OrderedDict()}),
            OrderedDict({'name':'PoS-MultiPoS', 'data':OrderedDict()}),
            OrderedDict({'name':'MultiPoS-MultiPoS', 'data': OrderedDict()})
        ]
        #self.verbform = OrderedDict()
        #self.pos_pos = OrderedDict()
        #self.subpos_all = OrderedDict()
        #self.pos_all = OrderedDict()
        #self.pos_multipos = OrderedDict()
        #self.multipos_multipos = OrderedDict()
        self.sent_raw = OrderedDict()

        if lang == 'en':
            """remove function valid only for swedish"""
            self.functions['VERBFORM'] = [
                ('Modal VERB to VERB', verbs_to_verbs, {'verb_type':'AUX'}),
                ('Present Participle to VERB', verbs_to_verbs, {'verb_type':'Pres_part'}),
                ('Past Participle to VERB', verbs_to_verbs, {'verb_type':'Past_part'}),
                ('Present VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRS'}),
                ('Past VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRT'}),
                ('Supine VERB to VERB', verbs_to_verbs, {'verb_type':'VB|SUP'}),
                # ('S-VERB to VERB', s_verbs_incsc, {"verb":True}) #Swedish only
            ]
            
            self.functions['SubPoS_ALL'] = [
                #('S-VERB INCSC', s_verbs_incsc, {}),                        #swedish only
                #('Neuter Gender NOUN INCSC', neuter_gender_noun_incsc, {}), #swedish only
                ('S-VERB INCSC', thirdSG_pronoun_incsc, {})                 #english only 
            ]
        elif lang == 'sv':
            """remove function valid only for english"""
            self.functions['VERBFORM'] = [
                ('Modal VERB to VERB', verbs_to_verbs, {'verb_type':'AUX'}),
                ('Present Participle to VERB', verbs_to_verbs, {'verb_type':'Pres_part'}),
                ('Past Participle to VERB', verbs_to_verbs, {'verb_type':'Past_part'}),
                ('Present VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRS'}),
                ('Past VERB to VERB', verbs_to_verbs, {'verb_type':'VB|PRT'}),
                ('Supine VERB to VERB', verbs_to_verbs, {'verb_type':'VB|SUP'}),
                ('S-VERB to VERB', s_verbs_incsc, {"verb":True}) #Swedish only
            ]
            self.functions['SubPoS_ALL'] = [
                ('S-VERB INCSC', s_verbs_incsc, {}),                        #swedish only
                ('Neuter Gender NOUN INCSC', neuter_gender_noun_incsc, {}), #swedish only
                #('S-VERB INCSC', thirdSG_pronoun_incsc, {})                 #english only 
            ]
            
        self.categories = [
            ('VERBFORM', self.feats[0]['data']),('PoS-PoS', self.feats[1]['data']), \
            ('SubPoS-ALL', self.feats[2]['data']), ('PoS-ALL', self.feats[3]['data']),\
            ('PoS-MultiPoS', self.feats[4]['data']), \
            ('MultiPoS-MultiPoS', self.feats[5]['data'])
        ]

        """
        self.categories = [
            ('VERBFORM', self.verbform),('PoS_PoS', self.pos_pos), \
            ('SubPoS_ALL', self.subpos_all), ('PoS_ALL', self.pos_all),\
            ('PoS_MultiPoS', self.pos_multipos), \
            ('MultiPoS_MultiPoS', self.multipos_multipos)
        ]
        """
        
        for category_name, feature_list in self.categories:
            if algorithm == '':
                for name, func, kwarg in self.functions[category_name]:
                    if level == 'sent':
                        c, t = func(content, **kwarg)
                    elif level in ['text','para']:
                        c, t, sent_scalars =0, 0, []
                        for sent in content.sentences:
                            sc, st = eval_str(sent.morph)['feats'][self.dict2index[category_name]]['data']['$'.join([name, 'raw'])]
                            c += sc
                            t += st
                            sent_scalars.append(eval_str(sent.morph)['feats'][self.dict2index[category_name]]['data'][name])
                        self.sent_raw[name] = sent_scalars                            

                    elif level == 'texts':
                        c, t = 0, 0
                        for text in content:
                            sc, st = eval_str(text.morph)['feats'][self.dict2index[category_name]]['data']['$'.join([name, 'raw'])]
                            c += sc
                            t += st                    
                    
                    scalar = round(c/t*1000, 2) if t else 1000 #set 1000 as the ceiling
                    feature_list[name] = scalar
                    feature_list['$'.join([name, 'raw'])] = c, t
                    
            elif algorithm == 'average':
                for name, _, _ in self.functions[category_name]:
                    values = []
                    if level != 'texts':
                        for sentence in content.sentences:
                            values.append(eval_str(sentence.morph)['feats'][self.dict2index[category_name]]['data'][name])
                        feature_list[name] = {'mean':mean(values), 'median':median(values)}
                    else:
                        for text in content:
                            values.extend(eval_str(text.morph)['sent_raw'][name])
                        feature_list[name] = {'mean':mean(values), 'median':median(values)}
                
