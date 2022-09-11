#!/usr/bin/env/ python3
#encoding: utf-8

from collections import OrderedDict, defaultdict
from .statistics import mean, median, get_text_list
from django.http import JsonResponse
from ..models import Paragraph
from .helpers import eval_str
import re

"""
The general features include:
token
word
word length
spelling error
sentences
sentence length (n words) (excluding punctuations)
paragraphs
paragraph length (n words) (excluding punctuations)
paragraph length (n sentences)
"""



def _syllable_count_en(word):
    word = word.lower()
    count = 0
    vowels = "aoueiy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count


def _syllable_count_sv(word):
    word = word.lower()
    vowels = 'aoueiyåöä'
    found_vowels = [b for b in word if b in vowels]
    if found_vowels:
        if not re.search('journalist', word): # journalist is the exceptional word where ou is counted as one syllable.
            return len(found_vowels)
        return len(found_vowels) - 1
    return 1
    

def merge_length_list(lists):
    res_list = []
    for l in lists:
        if len(res_list) < len(l):
            res_list[len(res_list):] = [0] * (len(l)-len(res_list))
        for length, num in enumerate(l):
            res_list[length] += num
    return res_list

def merge_defaultdicts_list(dicts):
    keys = [key for d in dicts for key in d.keys()]
    res_dict = defaultdict(list)
    for key in set(keys):
        res_dict[key] = merge_length_list([d[key] for d in dicts])
    return res_dict

def merge_defaultdicts(dicts): #assumption: int, sum values with the same key
    keys = [key for d in dicts for key in d.keys()]  
    res_dict = defaultdict(int)
    for key in set(keys):
        for d in dicts:
            res_dict[key] += d.get(key, 0)
    return res_dict



def count_helper(blocks): #blocks refer to sentences or paragraphs
    chars = sum([eval_str(block.general)['chars'] for block in blocks])
    tokens = sum([eval_str(block.general)['tokens'] for block in blocks])
    words = sum([eval_str(block.general)['words'] for block in blocks])
    syllables = sum([eval_str(block.general)['syllables'] for block in blocks])
    polysyllables = sum([eval_str(block.general)['polysyllables'] for block in blocks])
    misspells = sum([eval_str(block.general)['misspells'] for block in blocks])
    compounds = sum([eval_str(block.general)['compounds'] for block in blocks])
    token_len_list = [0] * max([len(eval_str(block.general)['token_len_list']) for block in blocks])
   
    sentence_len_list = []
    freq_form_dict_upos = merge_defaultdicts([eval_str(block.general)['freq_form_dict_upos'] for block in blocks])
    freq_norm_dict_upos = merge_defaultdicts([eval_str(block.general)['freq_norm_dict_upos'] for block in blocks])
    freq_lemma_dict_upos = merge_defaultdicts([eval_str(block.general)['freq_lemma_dict_upos'] for block in blocks])
    freq_form_dict_xpos = merge_defaultdicts([eval_str(block.general)['freq_form_dict_xpos'] for block in blocks])
    freq_norm_dict_xpos = merge_defaultdicts([eval_str(block.general)['freq_norm_dict_xpos'] for block in blocks])
    freq_lemma_dict_xpos = merge_defaultdicts([eval_str(block.general)['freq_lemma_dict_xpos'] for block in blocks])    

    types = set()
    for block in blocks:
        types = types.union(eval_str(block.general)['types'])
        for index, value in enumerate(eval_str(block.general)['token_len_list']):
            token_len_list[index] += value
        sentence_len_list.extend(eval_str(block.general)['sentence_len_list'])
    return [chars, tokens, words, syllables, polysyllables, types, \
            misspells, compounds, token_len_list, sentence_len_list, \
            freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
            freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos]

def generate_freq_list(d): #dict
    total = sum(d.values())
    freq_list = sorted(d.items(), key=lambda x:x[1], reverse=True)
    return [(index+1, key, value, round(value/total, 2)) for index, (key, value) in enumerate(freq_list)]

def get_args(content, level, _syllable_count_f=False):
    # def tag_length_helper(char_len, tag_len_list):
    #     if char_len+1 > len(tag_len_list):
    #         tag_len_list[len(tag_len_list):] = [0] * (char_len+1-len(tag_len_list))
    #         tag_len_list[char_len] = 1
    #     else:
    #         tag_len_list[char_len] += 1
    if level == 'sent':
        tokens = content.tokens
        sents = 1
        
        
        token_content = [(word.token_id, word.form, word.norm, word.lemma, \
                 word.xpos, word.upos) for word in tokens]
        
        polysyllables, syllables, types = 0,0, set()
        misspells, compounds = 0, 0

        token_len_list = []
        #pos_length = defaultdict(list) # to store frequence of words as well as each pos
        # upos_length = defaultdict(list)
        # xpos_length = defaultdict(list)

        freq_form_dict_upos = defaultdict(int)
        freq_norm_dict_upos = defaultdict(int)
        freq_lemma_dict_upos = defaultdict(int)
        freq_form_dict_xpos = defaultdict(int)
        freq_norm_dict_xpos = defaultdict(int)
        freq_lemma_dict_xpos = defaultdict(int)
        # upos_dict = defaultdict(int)
        # xpos_dict = defaultdict(int)
        #pos_dict = defaultdict(int)
        words = len(tokens)
        for token_id, form, norm, lemma, xpos, upos in token_content:
            freq_form_dict_upos['_'.join([form.lower(), upos])] += 1
            freq_norm_dict_upos['_'.join([norm.lower(), upos])] += 1
            freq_lemma_dict_upos['_'.join([lemma.lower(), upos])] += 1
            freq_form_dict_xpos['_'.join([form.lower(), xpos])] += 1
            freq_norm_dict_xpos['_'.join([norm.lower(), xpos])] += 1
            freq_lemma_dict_xpos['_'.join([lemma.lower(), xpos])] += 1
            
            if norm != '_':
                char_len = len(norm)
                s_len = _syllable_count_f(norm)
            else:
                char_len = len(form)
                s_len = _syllable_count_f(form)
            if len(token_len_list) > char_len:
              token_len_list[char_len] += 1
            else:
              token_len_list.extend([0]*(char_len-len(token_len_list))+[1])
            syllables += s_len
            if upos == 'PUNCT':
                words -= 1                
            if s_len > 2:
                polysyllables += 1
            if form != norm and norm != '_':
                misspells += 1
            if '-' in token_id:
                compounds += 1  
            types.add(norm.lower()) if norm != '_' else types.add(form.lower())          
        chars = sum([index*num for index, num in enumerate(token_len_list)])
        # chars = sum(token_len_list)
        tokens = len(tokens)
        sentence_len_list = [tokens]

    elif level in ['para', 'text']:
        #tokens = [token for sent in content.sentences for token in sent.token]
        sents = len(content.sentences)
        if level == 'para':
            chars, tokens, words, syllables, polysyllables, types, \
            misspells, compounds, token_len_list, sentence_len_list, \
            freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
            freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos = count_helper(content.sentences)  
        else:
            chars, tokens, words, syllables, polysyllables, types, \
            misspells, compounds, token_len_list, sentence_len_list, \
            freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
            freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos = count_helper(content.paragraphs)             

    elif level == 'texts':
        #tokens = [token for text in content for sent in text.sentences for token in sent.token]
        try:
            sents = sum([len(text.sentences) for text in content])
        except Exception:
            sents = sum([text.stats.number_of_sentences for text in content])
        chars, tokens, words, syllables, polysyllables, types, \
        misspells, compounds, token_len_list, sentence_len_list, \
        freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
        freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos = count_helper(content)             
    
    else:
        assert False, "Invalid level: " + level
  
    
    return [ chars, syllables, tokens, words, sents, polysyllables, list(types), \
           misspells, compounds, token_len_list, sentence_len_list, \
           freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
           freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos ]

def get_median(freq_list):
    def median_helper(target_index): #[0,1,2,3]
        end = 2 # start is index, which stands for the length of token
        total = sum(freq_list[1:3])
        if freq_list[1] >= target_index:
            return 1
        
        while total < target_index:
            end += 1
            total += freq_list[end]
        return end
    num = sum(freq_list)
    if num % 2 == 1: 
        total_index = num // 2 + 1
        return median_helper(total_index)      
    else:
        return (median_helper(num//2) + median_helper(num//2+1))/2



class Count_features:

    def __init__(self, content, lang, level='sent'):
        """
        feature scalars:
        token, type, spelling errors, compound
        sentent, paragraph,
        word length, sentence length, paragraph length
        """
        self.feats = OrderedDict()
        self.average = OrderedDict()
        _syllable_count_f = _syllable_count_en if lang == 'en' else _syllable_count_sv
        self.chars, self.syllables, self.tokens, self.words, self.sents, \
        self.polysyllables, self.types, self.misspells, \
        self.compounds, self.token_len_list, self.sentence_len_list, \
        self.freq_form_dict_upos, self.freq_norm_dict_upos, self.freq_lemma_dict_upos, \
        self.freq_form_dict_xpos, self.freq_norm_dict_xpos, self.freq_lemma_dict_xpos = get_args(content, level, _syllable_count_f)
        
        features = [
          ('Token-count', self.tokens), # token_count, {'punct':punct}, 'scalar'),
          ('Type-count', len(self.types)), #type_count, {'punct':punct}, 'raw'),
          ('Spelling errors', self.misspells), #misspells_count) #, {}, 'scalar'),
          ('Compound errors', self.compounds) # compound_count, {}, 'scalar'),
          ] #.length_count_char, {'punct':punct}, 'raw')
        if self.token_len_list:
            features.append(('Word length', [round(self.chars/self.tokens, 2), round(get_median(self.token_len_list),2)]))
        else:
            features.append(('Word length', [0,0])) 
        
        if level in ['para', 'text', 'texts']:
            features.append(('Sentences', self.sents)) # sentence_count, {}, 'scalar'))
            features.append(('Sentence length (n words)', \
                            [round(self.tokens/self.sents), round(median(self.sentence_len_list), 2)])) #length_count_word, {'punct':punct}, 'raw'))

        if level.startswith('text'):
            self.paragraph_len_list_word = []
            self.paragraph_len_list_sent = []
            if level == 'text':
                paragraph_list = content.paragraphs
            else:
                try:
                    paragraph_list = [ p for text in content for p in text.paragraphs ]
                except Exception:
                    paragraph_list = [ p for text in content for p in Paragraph.objects.all().filter(text=text) ]
            for para in paragraph_list:
                self.paragraph_len_list_word.append(eval_str(para.general)['tokens'])
                self.paragraph_len_list_sent.append(eval_str(para.general)['sents'])
            features.append(('Paragraphs', len(paragraph_list)))
            features.append(('Paragraph length (n words)', \
                            [round(self.tokens/len(paragraph_list), 2), \
                            round(median(self.paragraph_len_list_word), 2)]))#length_count_word, {}, 'raw'))
            features.append(('Paragraph length (n sentences)', \
                            [round(self.sents/len(paragraph_list), 2), \
                            round(median(self.paragraph_len_list_sent), 2)]))
        
        
        for feat, value in features:
            if isinstance(value, list):
                m1, m2 = value
                self.average[feat] = {'mean':m1, 'median':m2}
            else:
                self.feats[feat] = value
                scalar_list = False
                if feat.startswith('Sentence') or feat.startswith('Paragraph'):
                    continue
                if level == 'para':
                    scalar_list = [eval_str(sent.general)['feats'][feat] for sent in content.sentences]
                elif level == 'text':
                    scalar_list = [eval_str(para.general)['feats'][feat] for para in content.paragraphs]
                elif level == 'texts':
                    scalar_list = [eval_str(text.general)['feats'][feat] for text in content]
                if scalar_list:
                    self.average[feat] = {'mean': mean(scalar_list),'median':median(scalar_list)}

def get_content(request, level, text_id=False):
    text_list = get_text_list(request)
    if level == 'texts':
        content = text_list
    else:
        text = [text for text in text_list if str(text.id) == str(text_id)]
        if text:
            text = text[0]
            if level == 'para':
                content = text.paragraphs
            elif level == 'sent':
                content = text.sentences
            elif level == 'text':
                content = text
        else:
            content = None
    return content

def get_pos(request, poses, text_id=False, **kwarg):
    """
    #part of speech statistics
    #based on the counts of part of speech
    #the share and amount of pos
    {
        data type: pos_distribution
        data:{
            pos: (amount, share) 
        }
    }
    """
    context = OrderedDict()
    data = {'data_type':'pos_distribution','data':context}
    level = kwarg.get('level', 'texts')
    dict_name = kwarg.get('tagset', 'upos_dict')
    content = get_content(request, level, text_id)
    if not content:
        return JsonResponse(data)
    if level == 'texts':
        context = merge_defaultdicts([eval_str(text.general)[dict_name] for text in content])
    else:
        context = eval_str(content.general)['pos_dict']
    for pos in context:
        if pos not in poses:
            del context[pos]
    total = sum(context.values())
    context = OrderedDict({key:value for key,value in sorted(context.items(), key=lambda x:x[1], reverse=True)})
    for pos in context:
        context[pos] = context[pos], round(context[pos]/total*100, 2)
    return data


def get_tokens(request, word_type, poses, text_id=False, **kwargs):
    #based on the frequency list of form, norm respective lemma
    """
    {
        data_type:word-frequency,
        data:{
            index:index, token, pos, amount, share
        }
    }
    """
    #this function is not used yet and freq_%s_dict needs to be modified.
    level = kwargs.get('level', 'texts')
    content = get_content(request, level, text_id)
    context = {}
    data = {'data_type':'word_frequency','data':context}
    if level == 'texts':
        if word_type.lower() == 'form':
            context = merge_defaultdicts([eval_str(text.general)['freq_form_dict'] for text in content])
        elif word_type.lower() == 'norm':
            context = merge_defaultdicts([eval_str(text.general)['freq_norm_dict'] for text in content])
        elif word_type.lower() == 'lemma':
            context = merge_defaultdicts([eval_str(text.general)['freq_lemma_dict'] for text in content])
    else:
        if word_type.lower() == 'form':
            context = eval_str(content.general)['freq_form_dict']
        elif word_type.lower() == 'norm':
            context = eval_str(content.general)['freq_norm_dict']
        elif word_type.lower() == 'lemma':
            context = eval_str(content.general)['freq_lemma_dict']
    for word_pos in context:
        pos = word_pos.split('_')[-1]
        if pos not in poses:
            del context[word_pos]
    total = sum(context.values())
    context = OrderedDict({key:value for key,value in sorted(context.items(), key=lambda x:x[1], reverse=True)})
    data['data'] = OrderedDict()
    for index, word_pos in enumerate(context, 1):
        word, pos = word_pos.split('_')
        amount = context[word_pos]
        data['data'][index] = index, word, pos, amount, round(amount/total, 2)
    
    return data
