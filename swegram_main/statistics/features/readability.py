"""Readability features

English readability features:
Bilogarithm TTR
Root TTR
Coleman Liau Index
Flesch Reading Ease Grade Level
Flesch Kincaid
Automated Readability Index
SMOG

Swedish readability features:
LIX
OVIX
Typ-token ratio(rotbaserad)
Enkel nominalkvot
Full nominalkvot
"""
import math
from collections import defaultdict
from typing import Dict, List

from swegram_main.lib.utils import merge_dicts, merge_digits, mixin_merge_digits_or_dicts, r2, prepare_feature
from swegram_main.statistics.statistic_types import F


LONG_WORD_THRESHOLD = 6  # The threshold for being a long word


#########################################
# Readability functions for en and sv   #
#########################################
def root(types: int, tokens: int) -> float:
    """root type-token ratio ttr: t/sqrt(n)"""
    return r2(types, math.sqrt(tokens)) if tokens else 0.0


#########################################
# Readability functions for English     #
#########################################
def bilog(types: int, tokens: int) -> float:
    """type-token ratio bilogarithmic ttr: log t/log n"""
    try:
        return r2(math.log(types), math.log(tokens))
    except ZeroDivisionError:
        return r2(types, tokens)


def cli(sents: int, words: int, chars: int) -> float:
    """cli metric"""
    l = (chars / words) * 100
    s = (sents / words) * 100

    return r2((0.0588 * l) - (0.296 * s) - 15.8)


def fres(sents: int, words: int, syllables: int) -> float:
    """fres metric"""
    if not words:
        return 0.0
    return r2(206.835 - (1.015 * (words / sents)) - (84.6 * (syllables / words)))


def fkgl(sents: int, words: int, syllables: int) -> float:
    """fkgl metric"""
    if not words or not sents:
        return 0.0
    return r2(0.39 * (words / sents) + 11.8 * (syllables / words) - 15.59)


def ari(sents: int, words: int, chars: int) -> float:
    """ari metric"""
    if not words or not sents:
        return 0.0
    return r2(4.71 * (chars / words) + 0.5 * (words / sents) - 21.43)


def smog(sents: int, polysyllables: int) -> float:
    """smog metric"""
    if not sents:
        return 0.0
    return r2(1.0430 * (math.sqrt(polysyllables * (30 / sents)) + 3.1291))


#########################################
# Readability functions for Swedish     #
#########################################
def enkel_nominal_quota(xpos_dict: Dict[str, int]) -> float:
    """simple"""
    nn = xpos_dict.get("NN", 0)
    vb = xpos_dict.get("VB", 0)
    return r2(nn, vb) if vb else 0.0


def full_nominal_quota(xpos_dict: Dict) -> float:
    """full"""
    nn_pp_pc = sum(xpos_dict.get(pos, 0) for pos in ("PP", "NN", "PC"))
    pn_ab_vb = sum(xpos_dict.get(pos, 0) for pos in ("PN", "AB", "VB"))
    return r2(nn_pp_pc / pn_ab_vb) if pn_ab_vb else 0.0


def ovix(types: int, tokens: int) -> float:
    try:
        return r2(math.log(tokens), math.log(2 - math.log(types) / math.log(tokens)))
    except ZeroDivisionError:
        return 0.0


def lix(sents: int, words: int, word_dict: defaultdict) -> float:
    long_words = sum(v for k, v in word_dict.items() if len(k) > LONG_WORD_THRESHOLD)
    try:
        return r2(words / sents + long_words * 100 / words)
    except ZeroDivisionError:
        return 0.0


class ReadabilityFeatures:

    ASPECT = "readability"

    ENGLISH_FEATURES: List[F] = [
        prepare_feature(*args) for args in (
            (
                "Bilogarithm TTR", bilog, merge_digits,
                "types", "type_count", "attribute",
                "tokens", "token_count", "attribute"
            ),
            (
                "Root TTR", root, merge_digits,
                "types", "type_count", "attribute",
                "tokens", "token_count", "attribute"
            ),
            (
                "Coleman Liau Index", cli, merge_digits,
                "sents", "sents", "attribute",
                "words", "words", "attribute",
                "chars", "chars", "attribute"
            ),
            (
                "Flesch Reading Ease", fres, merge_digits,
                "sents", "sents", "attribute",
                "words", "words", "attribute",
                "syllables", "syllables", "attribute"
            ),
            (
                "Flesch Kincaid Grade level", fkgl, merge_digits,
                "sents", "sents", "attribute",
                "words", "words", "attribute",
                "syllables", "syllables", "attribute"
            ),
            (
                "Automated Readability Index", ari, merge_digits,
                "sents", "sents", "attribute",
                "words", "words", "attribute",
                "chars", "chars", "attribute"
            ),
            (
                "SMOG", smog, merge_digits,
                "sents", "sents", "attribute",
                "polysyllables", "polysyllables", "attribute",
            )
        )
    ]

    SWEDISH_FEATURES: List[F] = [
        prepare_feature(*args) for args in (
            (
                "LIX", lix, mixin_merge_digits_or_dicts,
                "sents", "sents", "attribute",
                "words", "words", "attribute",
                "word_dict", "word_dict", "attribute",
            ),
            (
                "OVIX", ovix, merge_digits,
                "types", "type_count", "attribute",
                "tokens", "token_count", "attribute"
            ),
            (
                "Typ-token ratio(rotbaserad)", root, merge_digits,
                "types", "type_count", "attribute",
                "tokens", "token_count", "attribute"
            ),
            (
                "Enkel nominalkvot", enkel_nominal_quota, merge_dicts,
                "xpos_dict", "xpos_dict", "attribute"
            ),
            (
                "Full nominalkvot", full_nominal_quota, merge_dicts,
                "xpos_dict", "xpos_dict", "attribute"
            )
        )
    ]
