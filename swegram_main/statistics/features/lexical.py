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
from typing import Dict, List, Optional, Tuple, TypeVar, Any, Union


from swegram_main.data.sentences import Sentence
from swegram_main.lib.utils import r2, mean, median, get_sum_for_field, merge_counter
from swegram_main.statistics.types import C, Feature


A = TypeVar("A", str, int)
K = TypeVar("K", bound=Dict[str, List[Tuple[str, Any]]])


def lemma_incsc(
    token_count: int, cefr_counter: Optional[Counter] = None, lemmas: Optional[A] = None, diff: bool = False
) -> float:
    if diff:
        return r2((token_count - sum(cefr_counter.values())) * 1000, token_count)
    if isinstance(lemmas, str):
        lemmas = cefr_counter.get(lemmas, 0)
    return r2(lemmas * 1000, token_count)


def _prepare_incsc(*args: str) -> Tuple[str, Dict[str, List[Tuple[str, Any]]]]:
    """Two arg types are defined in this case
    
    with arg as arg_type, it can be used in the incsc computation;
    with attribute as arg_type, it needs to be converted from the instance before it is utilized for computation
    """
    feature_name, *rest_args = args
    kwargs = {}
    while rest_args:
        try:
            arg_key, arg_value, arg_type, *rest_args = rest_args
            if arg_type in kwargs:
                kwargs[arg_type].append((arg_key, arg_value))
            else:
                kwargs[arg_type] = [(arg_key, arg_value)]
        except ValueError:
            raise Exception(f"Failed to parse args for feature, args: {args}")
    return feature_name, kwargs


class LexicalFeatures:

    COMMON_FEATURES = [
        _prepare_incsc(*args) for args in [
            ("A1 lemma INCSC", "lemmas", "1", "arg"),
            ("A2 lemma INCSC", "lemmas", "2", "arg"),
            ("B1 lemma INCSC", "lemmas", "3", "arg"),
            ("B2 lemma INCSC", "lemmas", "4", "arg"),
            ("C1 lemma INCSC", "lemmas", "5", "arg"),
            ("C2 lemma INCSC", "lemmas", "6", "arg"),
            ("Difficult Word INCSC", "lemmas", "advance_cefr", "attribute"),
            ("Difficult Noun or Verb INCSC", "lemmas", "advance_noun_or_verb", "attribute"),
            ("Out of Kelly-list INCSC", "diff", True, "arg")
        ]
    ]

    KELLY_LOG_FREQ_FEATURE = "Kelly log-frequency"
    SWEDISH_FEATURES = [
        *COMMON_FEATURES,
        (KELLY_LOG_FREQ_FEATURE, {})
    ]
    def __init__(self, content: C, lang: str, sentence: Optional[Sentence] = None) -> None:
        self.blocks = content
        self.feats = OrderedDict()
        self.sentence = sentence

        if lang == "en":
            self._set_english_feats()
        elif lang == "sv":
            self._set_swedish_feats()
        else:
            raise Exception(f"Unknown working language: {lang}")

    def _set_english_feats(self) -> None:
        self._set_english_feats(self.COMMON_FEATURES)

    def _set_swedish_feats(self) -> None:
        self._set_feats(self.SWEDISH_FEATURES)

    def _parse_args(self, kwarg_list: K, func: callable, content: Union[Sentence, C]) -> Dict[str, Any]:
        args = kwarg_list.get("arg", [])
        args.extend([
            (
                key,
                func(content, attribute)
            ) for key, attribute in kwarg_list.get("attribute", [])
        ])
        return {key: value for key, value in args}


    def _set_feats(self, features: Tuple[str, Optional[str], bool]) -> None:
        for feature_name, kwarg_list in features:
            if feature_name == self.KELLY_LOG_FREQ_FEATURE:
                if not self.sentence:
                    kelly_log_counter = merge_counter(self.blocks, "wpm_sv_counter")
                else:
                    kelly_log_counter = self.sentence.general.wpm_sv_counter
                self.feats[feature_name] = Feature(mean=mean(kelly_log_counter), median=median(kelly_log_counter))
                continue

            if not self.sentence:
                token_count = get_sum_for_field(self.blocks, "token_count")
                cefr_counter = merge_counter(self.blocks, "cefr_counter")
                kwargs = self._parse_args(kwarg_list, get_sum_for_field, self.blocks)
                scalar_list = [block.lexical.feats[feature_name].scalar for block in self.blocks]
                self.feats[feature_name] = Feature(
                    scalar=lemma_incsc(token_count, cefr_counter, **kwargs),
                    mean=mean(scalar_list), median=median(scalar_list)
                )

            else:
                token_count, cefr_counter = [getattr(self.sentence.general, a) for a in ["token_count", "cefr_counter"]]
                kwargs = self._parse_args(kwarg_list, getattr, self.sentence.general)
                self.feats[feature_name] = Feature(scalar=lemma_incsc(token_count, cefr_counter, **kwargs))
