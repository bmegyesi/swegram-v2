"""Syntactical features:

Dependency length
Dependency arcs longer than 5
Longest dependency length
Ratio of right dependency arcs
Ratio of left dependency arcs
Modifier variation
Pre-modifier INCSC
Post-modifier INCSC
Subordinate INCSC
Relative clause INCSC
Prepositional complement INCSC
"""
from collections import OrderedDict
from typing import Optional, Union, List, TypeVar, Dict, Any, Tuple

from swegram_main.config import LONG_ARC_THRESHOLD
from swegram_main.data.features import Feature
from swegram_main.data.sentences import Sentence
from swegram_main.lib.utils import mean, median, r2, prepare_feature, merge_digits, parse_args, incsc
from swegram_main.statistics.types import C


CI = TypeVar("CI", int, List[int], List[Tuple[int, ...]])  # Conver Tuple to List[int]
D = TypeVar("D", int, List[int], List[Tuple[int, ...]], List[List[Tuple[int, ...]]])  # Depth of a token in relation to root
K = TypeVar("K", bound=Dict[str, List[Tuple[str, Any]]])


def ratio(c: int, t: int) -> float:
    return r2(c * 100, t)


def modifier_incsc(pre_modifier: int, post_modifier: int, token_count: int) -> float:
    return incsc(pre_modifier + post_modifier, token_count)


def _convert_depth_list(iterable: CI) -> List[int]:
    if isinstance(iterable[0], tuple):
        return [len(e) for e in iterable]
    return iterable


def _sum(iterable: List[D]) -> int:
    """allow sum to take kwarg as well"""
    if isinstance(iterable, int):
        return iterable
    elif isinstance(iterable[0], list):
        return sum([_sum(i) for i in iterable])
    return sum(_convert_depth_list(iterable))


def _max(iterable: List[D]) -> int:
    """allow max to take kwarg as well"""
    if isinstance(iterable, int):
        return iterable
    elif isinstance(iterable[0], list):
        return max([_max(i) for i in iterable])
    return max(_convert_depth_list(iterable))


class SyntacticFeatures:

    FEATURES = [
        prepare_feature(*args) for args in [
            (
                "Dependency length", _sum, merge_digits,
                "iterable", "depth_list", "attribute",
                "operation", _max, "attribute_arg"
            ),
            (
                f"Dependency arcs longer than {LONG_ARC_THRESHOLD}", _sum, merge_digits,
                "iterable", "long_arcs", "attribute",
                "operation", _max, "attribute_arg"
            ),
            (
                "Longest dependency length", _max, merge_digits,
                "iterable", "depth_list", "attribute",
                "operation", _max, "attribute_arg"
            ),
            (
                "Ratio of right dependency arcs", ratio, merge_digits,
                "c", "right_arcs", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Ratio of left dependency arcs", ratio, merge_digits,
                "c", "left_arcs", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Modifier variation", modifier_incsc, merge_digits,
                "pre_modifier", "pre_modifier", "attribute",
                "post_modifier", "post_modifier", "attribute",
                "token_count", "token_count", "attribute"
            ),
            (
                "Pre-modifier INCSC", incsc, merge_digits,
                "c", "pre_modifier", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Post-modifier INCSC", incsc, merge_digits,
                "c", "post_modifier", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Subordinate INCSC", incsc, merge_digits,
                "c", "subordinate_nodes", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Relative clause INCSC", incsc, merge_digits,
                "c", "relative_clause_nodes", "attribute",
                "t", "token_count", "attribute"
            ),
            (
                "Prepositional complement INCSC", incsc, merge_digits,
                "c", "preposition_nodes", "attribute",
                "t", "token_count", "attribute"
            ),
        ]
    ]

    def __init__(self, content: C, lang: str, sentence: Optional[Sentence] = None) -> None:
        self.blocks = content
        self.data = OrderedDict()
        self.sentence = sentence
        self._set_feats()

    def _set_feats(self):
        for feature_name, func, attr_func, kwarg_list, attribute_kwargs in self.FEATURES:
            if self.sentence:
                kwargs = parse_args(kwarg_list, getattr, self.sentence.general)
                self.data[feature_name] = Feature(scalar=func(**kwargs))
            else:
                kwargs = parse_args(kwarg_list, attr_func, self.blocks, **attribute_kwargs)
                scalar_list = [block.syntactic[feature_name].scalar for block in self.blocks]
                self.data[feature_name] = Feature(
                    scalar=func(**kwargs), mean=mean(scalar_list), median=median(scalar_list)
                )
