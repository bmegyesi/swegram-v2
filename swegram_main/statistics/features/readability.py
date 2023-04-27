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
from collections import OrderedDict, defaultdict
from typing import Dict, List, Tuple, TypeVar, Optional

from swegram_main.data.sentences import Sentence
from swegram_main.statistics.types import B, C

from swegram_main.lib.utils import mean, median, r2


LONG_WORD_THRESHOLD = 6  # The threshold for being a long word
F = TypeVar("F", bound=Tuple[str, callable, Tuple[str, ...]])  # feature setting


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


def smog(sents: int, polysyllables: int):
    """smog metric"""
    if not sents:
        return 0.0
    return r2(1.0430 * (math.sqrt(polysyllables * (30 / sents)) + 3.1291))


#########################################
# Readability functions for Swedish     #
#########################################
def enkel_nominal_quota(pos_dict: Dict[str, int]) -> float:
    """simple"""
    nn = pos_dict.get("NN", 0)
    vb = pos_dict.get("VB", 0)
    return r2(nn, vb) if vb else 0.0


def full_nominal_quota(pos_dict: Dict) -> float:
    """full"""
    nn_pp_pc = sum([pos_dict.get(pos, 0) for pos in ["PP", "NN", "PC"]])
    pn_ab_vb = sum([pos_dict.get(pos, 0) for pos in ["PN", "AB", "VB"]])
    return r2(nn_pp_pc / pn_ab_vb) if pn_ab_vb else 0.0


def ovix(types: int, tokens: int) -> float:
    try:
        return r2(math.log(tokens), math.log(2 - math.log(types) / math.log(tokens)))
    except ZeroDivisionError:
        return 0.0


def lix(sents: int, words: int, freq_norm_dict: defaultdict) -> float:
    long_words = sum([v for k, v in freq_norm_dict.items() if len(k) > LONG_WORD_THRESHOLD])
    try:
        return r2(words / sents + long_words * 100 / words)
    except ZeroDivisionError:
        return 0.0


class ReadabilityFeatures:

    ENGLISH_FEATURES: Tuple[str, callable, Tuple[str, ...]] = (
        ("Bilogarithm TTR", bilog, ("type_count", "token_count")),
        ("Root TTR", root, ("type_count", "token_count")),
        ("Coleman Liau Index", cli, ("sents", "words", "chars")),
        ("Flesch Reading Ease", fres, ("sents", "words", "syllables")),
        ("Flesch Kincaid Grade level", fkgl, ("sents", "words", "syllables")),
        ("Automated Readability Index", ari, ("sents", "words", "chars")),
        ("SMOG", smog, ("sents", "polysyllables"))
    )

    SWEDISH_FEATURES: Tuple[str, callable, Tuple[str, ...]] = (
        ("LIX", lix, ("sents", "words", "word_dict")),
        ("OVIX", ovix, ("type_count", "token_count")),
        ("Typ-token ratio(rotbaserad)", root, ("type_count", "token_count")),
        ("Enkel nominalkvot", enkel_nominal_quota, ("xpos_dict", )),
        ("Full nominalkvot", full_nominal_quota, ("xpos_dict", ))
    )

    def __init__(self, content: List[B], lang: str, sentence: Optional[Sentence] = None) -> None:
        self.blocks = content
        self.lang = lang
        self.feats = OrderedDict()
        self.sentence = sentence
        if not self.sentence:
            self.average = OrderedDict()
        

        if lang == "en":
            self._set_english_feats()
        elif lang == "sv":
            self._set_swedish_feats()
        else:
            raise Exception(f"Unknown working language: {lang}")

    def _set_feats(self, features: F) -> None:
        for feature_name, function, arguments in features:
            if self.sentence:
                self.feats[feature_name] = function(*[getattr(self.sentence.general, arg) for arg in arguments])
            else:
                self.feats[feature_name] = function(*[_get_attr(self.blocks, arg) for arg in arguments])
                scalar_list = [b.readability.feats[feature_name] for b in self.blocks]
                self.average[feature_name] = {"mean": mean(scalar_list), "median": median(scalar_list)}

    def _set_english_feats(self) -> None:
        self._set_feats(self.ENGLISH_FEATURES)

    def _set_swedish_feats(self) -> None:
        self._set_feats(self.SWEDISH_FEATURES)


def _get_attr(instances: List[C], attribute_name: str):
    element_values = [getattr(instance.general, attribute_name) for instance in instances]
    if isinstance(element_values[0], defaultdict):
        return _merge_dicts(element_values)
    return sum(element_values)


def _merge_dicts(blocks: List[object]) -> defaultdict:
    df = defaultdict(int)
    for block in blocks:
        for key, value in block.items():
            df[key] += value
    return df
