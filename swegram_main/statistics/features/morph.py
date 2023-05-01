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
from swegram_main.data.sentences import Sentence
from swegram_main.lib.utils import r2, mean, median, get_logger, merge_digits_for_fields
from swegram_main.statistics.types import C


logger = get_logger(__name__)
SCF = Tuple[str, Tuple[str, List[str], List[str]], bool] # Single Common Feature
CF = TypeVar("CF", bound=List[Tuple[str, List[SCF]]])  # Common Features
TARGET = TypeVar("TARGET", str, int)

SINGLE_PSOS = ["ADJ", "ADV", "NOUN", "PART", "PUNCT", "SCONJ", "VERB"] 
VARIATION_PSOS_BASE = ["ADJ", "ADV", "NOUN", "VERB"]
LEXICAL_PSOS = [*VARIATION_PSOS_BASE, "PROPN", "INTJ"]
FUNCTIONAL_PSOS = ["ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "PUNCT", "SCONJ", "SYM", "X"]


def _get_psos_amount(pos_dicts: List[defaultdict], psos: List[str]) -> int:
    return sum([pos_dict[pos] for pos_dict in pos_dicts for pos in psos])


def _serilize_psos(psos: Union[str, List[str]]):
    if isinstance(psos, str):
        return psos.split()
    return psos


def pos_incsc(pos_dicts: List[defaultdict], target_psos: List[TARGET], base_psos: List[str]) -> float:
    """get incsc value (a ratio) by retreiving the amount of target parts of speech and base parts of speech
    from pos dictionary
    """
    try:
        if isinstance(target_psos[0], int):
            target_amount = sum(target_psos)
        else:
            target_amount = _get_psos_amount(pos_dicts, target_psos)
        return r2(1000 * target_amount, _get_psos_amount(pos_dicts, base_psos))
    except ZeroDivisionError:
        # logger.warning(f"The amount of base parts of speech is zero: {base_psos}.")
        return 1000.00


def _prepare_incsc(
    feature_name: str, target: str,  # target is pos, pos array, feat, or feat array
    base_psos: Union[str, List[str]] = UD_TAGS, dict_type: str = "upos_dict", convert_feat: bool = False,
) -> SCF:
    return feature_name, (dict_type, _serilize_psos(target), _serilize_psos(base_psos), convert_feat)


class MorphFeatures:

    MORPH_GROUPS = ["VERBFORM", "PoS-PoS", "SubPoS-ALL", "PoS-ALL", "PoS-MultiPoS", "MultiPoS-MultiPoS"]
    _COMMON_VERBFORM_FEATURES = [
        _prepare_incsc("Modal VERB to VERB", "AUX", "AUX VERB"),
        _prepare_incsc("Present Participle to VERB", "pres_pc", "AUX VERB", convert_feat=True),
        _prepare_incsc("Past Participle to VERB", "past_pc", "AUX VERB", convert_feat=True),
        _prepare_incsc("Present VERB to VERB", "pres_verb", "AUX VERB", convert_feat=True),
        _prepare_incsc("Past VERB to VERB", "past_verb", "AUX VERB", convert_feat=True),
        _prepare_incsc("Supine VERB to VERB", "sup_verb", "AUX VERB", convert_feat=True)
    ]

    _COMMON_FEATURES: CF = [
        ("PoS-ALL", [_prepare_incsc(f"{pos} INCSC", pos) for pos in SINGLE_PSOS]),
        ("PoS-PoS", [
            _prepare_incsc("NOUN to VERB", "NOUN", "VERB"),
            _prepare_incsc("PRON to NOUN", "PRON", "NOUN"),
            _prepare_incsc("PRON to PREP", "PRON", "PREP"),
        ]),
        ("PoS-MultiPoS", [
            _prepare_incsc(f"{pos} Variation", pos, VARIATION_PSOS_BASE)
            for pos in VARIATION_PSOS_BASE
        ]),
        ("MultiPoS-MultiPoS", [
            _prepare_incsc("CCONJ & SCONJ INCSC", "CCONJ SCONJ"),
            _prepare_incsc("Functional Token INCSC", FUNCTIONAL_PSOS),
            _prepare_incsc("Lex to Non-Lex", LEXICAL_PSOS, FUNCTIONAL_PSOS),
            _prepare_incsc("Lex to Token", LEXICAL_PSOS),
            _prepare_incsc("Nominal Ratio", "NN PC PP", "AB PN VB", dict_type="xpos_dict"),
            _prepare_incsc("Rel INCSC",  "rel_pron", convert_feat=True)
        ])
    ]

    SWEDISH_FEATURES: CF = [
        ("VERBFORM", [
            *_COMMON_VERBFORM_FEATURES,
            _prepare_incsc("S-VERB to VERB", "s_verb", "AUX VERB", convert_feat=True)
        ]),
        *_COMMON_FEATURES,
        ("SubPoS-ALL", [
            _prepare_incsc("S-VERB INCSC", "s_verb", convert_feat=True),
            _prepare_incsc("Neuter Gender NOUN INCSC", "neut_noun", convert_feat=True)
        ])
    ]

    ENGLISH_FEATUERS: CF = [
        ("VERBFORM", _COMMON_VERBFORM_FEATURES),
        *_COMMON_FEATURES,
        ("SubPoS-ALL", [
            _prepare_incsc("S-VERB INCSC", "_3sg_pron", convert_feat=True)
        ])
    ]

    def __init__(self, content: C, lang: str, sentence: Optional[Sentence] = None) -> None:
        self.blocks = content
        self.feats = [OrderedDict({"name": group, "data": OrderedDict()}) for group in self.MORPH_GROUPS]
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

    def _set_feats(self, features: CF):
        for index, (_, feature_list) in enumerate(features):
            for feature_name, (dict_type, target_list, base_psos, to_convert) in feature_list:
                if not self.sentence:
                    if to_convert:
                        target_list = merge_digits_for_fields(self.blocks, target_list)
                    self.feats[index]["data"][feature_name] = {
                        "scalar": pos_incsc(
                            [getattr(block.general, dict_type) for block in self.blocks],
                            target_list, base_psos
                        )
                    }
                    scalars = [b.morph.feats[index]["data"][feature_name]["scalar"] for b in self.blocks]
                    self.feats[index]["data"][feature_name].update({"mean": mean(scalars), "median": median(scalars)})
                else:
                    if to_convert:
                        target_list = [getattr(self.sentence.general, feature) for feature in target_list]
                    self.feats[index]["data"][feature_name] = {
                        "scalar": pos_incsc([getattr(self.sentence.general, dict_type)], target_list, base_psos)
                    }
