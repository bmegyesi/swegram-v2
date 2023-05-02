"""Morphological features:

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
from collections import OrderedDict, defaultdict
from typing import Optional, List, Tuple, TypeVar, Union

from swegram_main.config import UD_TAGS
from swegram_main.data.features import Feature
from swegram_main.data.sentences import Sentence
from swegram_main.lib.utils import r2, mean, median, get_logger, prepare_feature, parse_args
from swegram_main.lib.utils import incsc, mixin_merge_digits_or_dicts
from swegram_main.statistics.types import C


logger = get_logger(__name__)
TARGET = TypeVar("TARGET", str, int)

SINGLE_PSOS = ["ADJ", "ADV", "NOUN", "PART", "PUNCT", "SCONJ", "VERB"] 
VARIATION_PSOS_BASE = ["ADJ", "ADV", "NOUN", "VERB"]
VARIATION_PSOS_BASE_STRING = " ".join(VARIATION_PSOS_BASE)
LEXICAL_PSOS = " ".join([*VARIATION_PSOS_BASE, "PROPN", "INTJ"])
FUNCTIONAL_PSOS = " ".join(["ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "PUNCT", "SCONJ", "SYM", "X"])
UD_TAG_STRING = " ".join(UD_TAGS)


def prepare_verb(group_name: str, feature_name: str, *args, dict_type: str = "upos_dict") -> Tuple[str, callable, callable, str, str]:
    return f"{group_name}_{feature_name}", pos_incsc, mixin_merge_digits_or_dicts, *args, "pos_dict", dict_type, "attribute"


def _psos_counter(psos: str, pos_dict: defaultdict) -> int:
    return sum([pos_dict[pos] for pos in psos.split()])


def pos_incsc(target_psos: Union[str, int], base_psos: str, pos_dict: defaultdict) -> float:
    targets = _psos_counter(target_psos, pos_dict) if isinstance(target_psos, str) else target_psos
    return incsc(targets, _psos_counter(base_psos, pos_dict))


class MorphFeatures:

    MORPH_GROUPS = ["VERBFORM", "PoS-PoS", "SubPoS-ALL", "PoS-ALL", "PoS-MultiPoS", "MultiPoS-MultiPoS"]
    _COMMON_VERBFORM_FEATURES = [
        prepare_feature(*prepare_verb("VERBFORM", *args)) for args in [
            (
                "Modal VERB to VERB",
                "target_psos", "AUX", "arg",
                "base_psos", "AUX VERB", "arg"
            ),
            (
                "Present Participle to VERB",
                "target_psos", "pres_pc", "attribute",
                "base_psos", "AUX VERB", "arg"
            ),
            (
                "Past Participle to VERB",
                "target_psos", "past_pc", "attribute",
                "base_psos", "AUX VERB", "arg"
            ),
            (
                "Present VERB to VERB",
                "target_psos", "pres_verb", "attribute",
                "base_psos", "AUX VERB", "arg"
            ),
            (
                "Past VERB to VERB",
                "target_psos", "past_verb", "attribute",
                "base_psos", "AUX VERB", "arg"
            ),
            (
                "Supine VERB to VERB",
                "target_psos", "sup_verb", "attribute",
                "base_psos", "AUX VERB", "arg"
            )
        ]
    ]

    _COMMON_FEATURES = [
        *[
            prepare_feature(
                *prepare_verb(
                    "PoS-ALL", f"{pos} INCSC",
                    "target_psos", pos, "arg",
                    "base_psos", UD_TAG_STRING, "arg"
                )
            ) for pos in SINGLE_PSOS
        ],
        *[
            prepare_feature(*prepare_verb("PoS-PoS", *args)) for args in [
                (
                    "NOUN to VERB",
                    "target_psos", "NOUN", "arg",
                    "base_psos", "VERB", "arg"
                ),
                (
                    "PRON to NOUN",
                    "target_psos", "PRON", "arg",
                    "base_psos", "NOUN", "arg"
                ),
                (
                    "PRON to PREP",
                    "target_psos", "PRON", "arg",
                    "base_psos", "PREP", "arg"
                )
            ]
        ],
        *[
            prepare_feature(
                *prepare_verb(
                    "PoS-MultiPoS", f"{pos} Variation",
                    "target_psos", pos, "arg",
                    "base_psos", VARIATION_PSOS_BASE_STRING, "arg"
                )
            ) for pos in VARIATION_PSOS_BASE
        ],
        *[
            prepare_feature(*prepare_verb("MultiPoS-MultiPoS", *args, dict_type=dict_type)) for dict_type, *args in [
                (
                    "upos_dict", "CCONJ & SCONJ INCSC",
                    "target_psos", "CCONJ SCONJ", "arg",
                    "base_psos", UD_TAG_STRING, "arg"
                ),
                (
                    "upos_dict", "Functional Token INCSC",
                    "target_psos", FUNCTIONAL_PSOS, "arg",
                    "base_psos", UD_TAG_STRING, "arg"
                ),
                (
                    "upos_dict", "Lex to Non-Lex",
                    "target_psos", LEXICAL_PSOS, "arg",
                    "base_psos", FUNCTIONAL_PSOS, "arg"
                ),
                (
                    "upos_dict", "Lex to Token",
                    "target_psos", LEXICAL_PSOS, "arg",
                    "base_psos", UD_TAG_STRING, "arg"
                ),
                (
                    "xpos_dict", "Nominal Ratio",
                    "target_psos", "NN PC PP", "arg",
                    "base_psos", "AB PN VB", "arg"
                ),
                (
                    "upos_dict", "Rel INCSC",
                    "target_psos", "rel_pron", "attribute",
                    "base_psos", UD_TAG_STRING, "arg"
                ),
            ]
        ]
    ]

    SWEDISH_FEATURES = [
        *_COMMON_VERBFORM_FEATURES,
        prepare_feature(
            *prepare_verb(
                "VERBFORM", "S-VERB to VERB",
                "target_psos", "s_verb", "attribute",
                "base_psos", "AUX VERB", "arg"
            )
        ),
        *_COMMON_FEATURES,
        *[
            prepare_feature(*prepare_verb("SubPoS-ALL", *args)) for args in [
                (
                    "S-VERB INCSC",
                    "target_psos", "s_verb", "attribute",
                    "base_psos", UD_TAG_STRING, "arg"
                ),
                (
                    "Neuter Gender NOUN INCSC",
                    "target_psos", "neut_noun", "attribute",
                    "base_psos", UD_TAG_STRING, "arg"
                )
            ]
        ]
    ]

    ENGLISH_FEATUERS = [
        *_COMMON_VERBFORM_FEATURES,
        *_COMMON_FEATURES,
        prepare_feature(
            *prepare_verb(
                "SubPoS-ALL", "S-VERB INCSC",
                "target_psos", "_3sg_pron", "attribute",
                "base_psos", UD_TAG_STRING, "arg"
            )
        )
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

    def _set_english_feats(self):
        self._set_english_feats(self.ENGLISH_FEATUERS)

    def _set_swedish_feats(self):
        self._set_feats(self.SWEDISH_FEATURES)
    
    def _set_feats(self, features):
        for feature_name, func, attr_func, kwarg_list, attribute_kwargs in features:
            if self.sentence:
                kwargs = parse_args(kwarg_list, getattr, self.sentence.general)
                self.data[feature_name] = Feature(scalar=func(**kwargs))
            else:
                kwargs = parse_args(kwarg_list, attr_func, self.blocks, **attribute_kwargs)
                scalar_list = [block.morph[feature_name].scalar for block in self.blocks]
                self.data[feature_name] = Feature(
                    scalar=func(**kwargs), mean=mean(scalar_list), median=median(scalar_list)
                )