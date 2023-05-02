"""Lexical features:

A1 lemma INCSC
A2 lemma INCSC
B1 lemma INCSC
B2 lemma INCSC
C1 lemma INCSC
C2 lemma INCSC
Difficult Word INCSC
Difficult Noun or Verb INCSC
Out of Kelly-list INCSC
Kelly log-frequency (Swedish only)
"""
from collections import Counter, OrderedDict
from typing import Dict, List, Optional, Tuple, TypeVar, Any


from swegram_main.data.features import Feature
from swegram_main.data.sentences import Sentence
from swegram_main.lib.utils import (
    mean, median, mixin_merge_digits_or_counters, merge_counters,
    r2, prepare_feature, parse_args
)
from swegram_main.statistics.types import C


A = TypeVar("A", str, int)
K = TypeVar("K", bound=Dict[str, List[Tuple[str, Any]]])
TOKEN_COUNT_ARG = ["token_count", "token_count", "attribute"]
CEFR_COUNT_ARG = ["cefr_counter", "cefr_counter", "attribute"]


def lemma_incsc(
    token_count: int, cefr_counter: Optional[Counter] = None, lemmas: Optional[A] = None, diff: bool = False
) -> float:
    if diff:
        return r2((token_count - sum(cefr_counter.values())) * 1000, token_count)
    if isinstance(lemmas, str):
        lemmas = cefr_counter.get(lemmas, 0)
    return r2(lemmas * 1000, token_count)


def prepare_lexical_features(*args):
    args = *args, *TOKEN_COUNT_ARG, *CEFR_COUNT_ARG
    return prepare_feature(*args)


class LexicalFeatures:

    ENGLISH_FEATURES = [
        prepare_lexical_features(*args) for args in [
            ("A1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "1", "arg"),
            ("A2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "2", "arg"),
            ("B1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "3", "arg"),
            ("B2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "4", "arg"),
            ("C1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "5", "arg"),
            ("C2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "6", "arg"),
            ("Difficult Word INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "advance_cefr", "attribute"),
            ("Difficult Noun or Verb INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "advance_noun_or_verb", "attribute"),
            ("Out of Kelly-list INCSC", lemma_incsc, mixin_merge_digits_or_counters, "diff", True, "arg")
        ]
    ]

    KELLY_LOG_FREQ_FEATURE = "Kelly log-frequency"
    SWEDISH_FEATURES = [
        *ENGLISH_FEATURES,
        prepare_feature("Kelly log-frequency", mean, merge_counters, "numbers", "wpm_sv_counter", "attribute")
    ]
    def __init__(self, content: C, lang: str, sentence: Optional[Sentence] = None) -> None:
        self.blocks = content
        self.data = OrderedDict()
        self.sentence = sentence

        if lang == "en":
            self._set_english_feats()
        elif lang == "sv":
            self._set_swedish_feats()
        else:
            raise Exception(f"Unknown working language: {lang}")

    def _set_english_feats(self) -> None:
        self._set_english_feats(self.ENGLISH_FEATURES)

    def _set_swedish_feats(self) -> None:
        self._set_feats(self.SWEDISH_FEATURES)

    def _set_feats(self, features) -> None:
        for feature_name, func, attr_func, kwarg_list, attr_kwargs in features:

            if self.sentence:
                kwargs = parse_args(kwarg_list, getattr, self.sentence.general)
                self.data[feature_name] = Feature(scalar=func(**kwargs))
            else:
                kwargs = parse_args(kwarg_list, attr_func, self.blocks, **attr_kwargs)
                scalar_list = [block.lexical[feature_name].scalar for block in self.blocks]
                self.data[feature_name] = Feature(
                    scalar=func(**kwargs),
                    mean=mean(scalar_list), median=median(scalar_list)
                )
