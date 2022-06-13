#!/usr/bin/env/ python3
#encoding: utf-8

"""
To extract readability features

lang: en
Bilogarithm TTR
Root TTR
Coleman Liau Index
Flesch Reading Ease Grade Level
Flesch Kincaid
Automated Readability Index
SMOG

lang: sv
LIX
OVIX
Typ-token ratio(rotbaserad)
Enkel nominalkvot
Full nominalkvot
"""

from collections import OrderedDict
import math

from django.http import JsonResponse

from ..config import SUC_TAGS
from .general_func import get_args, merge_defaultdicts
from .helpers import eval_str
from .statistics import mean, median


##################Readability functions for english###################
def bilog(types, tokens):
    # type-token ratio bilogarithmic ttr: log t/log n
    try:
        return round(math.log(types) / math.log(tokens), 2)
    except ZeroDivisionError:
        return round(types / tokens, 2)


def root(types, tokens):
    # root type-token ratio ttr: t/sqrt(n)
    return round(types / math.sqrt(tokens), 2) if tokens else 0.0


def cli(sents, words, chars):
    if not words:
        return 0.0
    l = (chars / words) * 100
    s = (sents / words) * 100

    cli = (0.0588 * l) - (0.296 * s) - 15.8

    return round(cli, 2)


def fres(sents, words, syllables):

    if not words:
        return 0.0
    return round(206.835 - (1.015 * (words/sents)) - (84.6 * (syllables/words)), 2)


def fkgl(sents, words, syllables):

    if not words or not sents:
        return 0.0
    return round(0.39 * (words / sents) + 11.8 * (syllables / words) - 15.59, 2)


def ari(chars, words, sents):

    if not words or not sents:
        return 0.0
    return round(4.71 * (chars / words) + 0.5 * (words/sents) - 21.43, 2)


def smog(sents, polysyllables):

    if not sents:
        return 0.0
    return round(1.0430 * (math.sqrt(polysyllables * (30/sents)) + 3.1291), 2)


##################Readability functions for swedish###################
def enkel_nominal_quota(pos_dict):
    # Return simple, full   simple: nn/vb; full: nn_pp_pc / pn_ab_vb
    nn = pos_dict.get('NN', 0)
    vb = pos_dict.get('VB', 0)
    return round(nn/vb, 2) if vb else 0.0


def full_nominal_quota(pos_dict):
    nn_pp_pc = sum([pos_dict.get(pos, 0) for pos in ['PP', 'NN', 'PC']])
    pn_ab_vb = sum([pos_dict.get(pos, 0) for pos in ['PN', 'AB', 'VB']])
    return round(nn_pp_pc/pn_ab_vb, 2) if pn_ab_vb else 0.0


def ovix(tokens, types):
    try:
        scalar = round(math.log(tokens)/math.log(2 -
                       (math.log(types)/math.log(tokens))), 2)
    except ZeroDivisionError:
        scalar = 0.0
    return scalar


def lix(words, sents, freq_norm_dict):
    long_words = sum(
        [value for key, value in freq_norm_dict.items() if len(key) > 6])
    try:
        f = round(words/sents + long_words*100/words, 2)
    except ZeroDivisionError:
        f = 0.0
    finally:
        return f


class Readability_features:

    def __init__(self, content, lang, level='sent'):
        """need to check out how syllable counting for swedish"""
        if level != 'texts':
            self.chars = eval_str(content.general)['chars']
            self.syllables = eval_str(content.general)['syllables']
            self.tokens = eval_str(content.general)['tokens']
            self.words = eval_str(content.general)['words']
            self.sents = eval_str(content.general)['sents']
            self.polysyllables = eval_str(content.general)['polysyllables']
            self.types = eval_str(content.general)['types']
        else:
            self.chars, self.syllables, self.tokens, self.words, self.sents, \
                self.polysyllables, self.types = get_args(content, level)[:7]

        if lang == 'en':
            features = [
                ('Bilogarithm TTR', bilog, {'types': len(
                    self.types), 'tokens': self.tokens}),
                ('Root TTR', root, {'types': len(
                    self.types), 'tokens': self.tokens}),
                ('Coleman Liau Index', cli, {
                 'sents': self.sents, 'words': self.words, 'chars': self.chars}),
                ('Flesch Reading Ease', fres, {
                 'sents': self.sents, 'words': self.words, 'syllables': self.syllables}),
                ('Flesch Kincaid Grade level', fkgl, {
                 'sents': self.sents, 'words': self.words, 'syllables': self.syllables}),
                ('Automated Readability Index', ari, {
                 'sents': self.sents, 'words': self.words, 'chars': self.chars}),
                ('SMOG', smog, {'sents': self.sents,
                 'polysyllables': self.polysyllables})
            ]

        elif lang == 'sv':
            if level != 'texts':
                freq_norm_dict_xpos = eval_str(content.general)[
                    'freq_norm_dict_xpos']
            else:
                freq_norm_dict_xpos = merge_defaultdicts(
                    [eval_str(text.general)['freq_norm_dict_xpos'] for text in content])

            features = [
                ('LIX', lix, {'words': self.words, 'sents': self.sents,
                 'freq_norm_dict': freq_norm_dict_xpos}),
                ('OVIX', ovix, {'tokens': self.tokens,
                 'types': len(self.types)}),
                ('Typ-token ratio(rotbaserad)', root,
                 {'types': len(self.types), 'tokens': self.tokens})
            ]

            pos_dict = {}
            for k, v in freq_norm_dict_xpos.items():
                pos = k.split('_')[-1]
                if pos not in SUC_TAGS:
                    continue
                if pos in pos_dict:
                    pos_dict[pos] += v
                else:
                    pos_dict[pos] = v

            if pos_dict:
                features.extend([
                    ('Enkel nominalkvot', enkel_nominal_quota,
                     {'pos_dict': pos_dict}),
                    ('Full nominalkvot', full_nominal_quota,
                     {'pos_dict': pos_dict})
                ])

        self.feats = OrderedDict()
        if level != 'sent':
            self.average = OrderedDict()

        """
        to allow the user to include punctuation or not
        kwargs = {
          'chars':self.chars, 'syllables':self.syllables, 'tokens':self.tokens, \
          'sents':self.sents, 'polysyllables':self.polysyllables, \
          'types':len(self.types), 'words':self.tokens
        }
        """

        """we use the one level lower scalars to compute the currenct feature scalar"""

        # if export is False:
        for name, func, kwargs in features:
            self.feats[name] = func(**kwargs)
            scalar_list = False

            if level == 'para':
                scalar_list = [eval_str(sent.readability)[
                    'feats'][name] for sent in content.sentences if name in eval_str(sent.readability)['feats']]
            elif level == 'text':
                scalar_list = [eval_str(para.readability)[
                    'feats'][name] for para in content.paragraphs if name in eval_str(para.readability)['feats']]
            elif level == 'texts':
                scalar_list = [eval_str(text.readability)[
                    'feats'][name] for text in content if name in eval_str(text.readability)['feats']]
            if scalar_list:
                self.average[name] = {'mean': mean(
                    scalar_list), 'median': median(scalar_list)}
