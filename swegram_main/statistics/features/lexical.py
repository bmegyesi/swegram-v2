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
from collections import Counter
from typing import List, Optional, Union

from swegram_main.lib.utils import mean, mixin_merge_digits_or_counters, merge_counters, r2, prepare_feature
from swegram_main.statistics.statistic_types import A, F


TOKEN_COUNT_ARG = ["token_count", "token_count", "attribute"]
CEFR_COUNT_ARG = ["cefr_counter", "cefr_counter", "attribute"]


def lemma_incsc(
    token_count: int, cefr_counter: Optional[Counter] = None,
    lemmas: Optional[A] = None, diff: bool = False
) -> float:
    if diff:
        return r2((token_count - sum(cefr_counter.values())) * 1000, token_count)
    if isinstance(lemmas, str):
        lemmas = cefr_counter.get(lemmas, 0)
    return r2(lemmas * 1000, token_count)


def prepare_lexical_features(*args: Union[str, callable]) -> F:
    args = *args, *TOKEN_COUNT_ARG, *CEFR_COUNT_ARG
    return prepare_feature(*args)


class LexicalFeatures:

    ASPECT = "lexical"

    ENGLISH_FEATURES: List[F] = [
        prepare_lexical_features(*args) for args in (
            ("A1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "1", "arg"),
            ("A2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "2", "arg"),
            ("B1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "3", "arg"),
            ("B2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "4", "arg"),
            ("C1 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "5", "arg"),
            ("C2 lemma INCSC", lemma_incsc, mixin_merge_digits_or_counters, "lemmas", "6", "arg"),
            (
                "Difficult Word INCSC", lemma_incsc, mixin_merge_digits_or_counters,
                "lemmas", "advance_cefr", "attribute"
            ),
            (
                "Difficult Noun or Verb INCSC", lemma_incsc, mixin_merge_digits_or_counters,
                "lemmas", "advance_noun_or_verb", "attribute"
            ),
            ("Out of Kelly-list INCSC", lemma_incsc, mixin_merge_digits_or_counters, "diff", True, "arg")
        )
    ]

    KELLY_LOG_FREQ_FEATURE = "Kelly log-frequency"
    SWEDISH_FEATURES: List[F] = [
        *ENGLISH_FEATURES,
        prepare_feature("Kelly log-frequency", mean, merge_counters, "numbers", "wpm_sv_counter", "attribute")
    ]
