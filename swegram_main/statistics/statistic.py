"""Model of statistic.py
Create a decorator to append statistic e.g. Text instance

"""
from collections import OrderedDict
from typing import Dict

from swegram_main.lib.utils import mean, median, parse_args
from swegram_main.data.features import Feature
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text, Corpus
from swegram_main.data.sentences import Sentence
from swegram_main.statistics.features.general import CountFeatures as CF
from swegram_main.statistics.features.lexical import LexicalFeatures as LF
from swegram_main.statistics.features.morph import MorphFeatures as MF
from swegram_main.statistics.features.readability import ReadabilityFeatures as RF
from swegram_main.statistics.features.syntactic import SyntacticFeatures as SF
from swegram_main.statistics.statistic_types import C, F


LINGUISTIC_ASPECTS = [RF, MF, LF, SF]  # CF is loaded separately


class InvalidWorkingLanguage(Exception):
    """Working language error"""

class InvalidLinguisticUnit(Exception):
    """Linguistic Unit Error"""


class StatisticLoading:

    def __init__(self, load_function: callable) -> None:
        self.function = load_function

    def __call__(self, *args, **kwargs) -> None:
        instance = self.function(*args, **kwargs)
        if "sv" in args:
            language = "sv"
        elif "en" in args:
            language = "en"
        else:
            raise InvalidWorkingLanguage(f"Only valid for en and sv, but got {language}.")

        # skip loading when the element doesn't exist in the instnace
        if not getattr(instance, instance.elements):
            return instance

        if isinstance(instance, (Sentence, Paragraph, Text, Corpus)):
            instance = CF().load_instance(instance, language)
            instance = load_statistic(instance, language)
        else:
            raise InvalidLinguisticUnit(f"Unknown instance type, excepted to get Sentence, Paragraph, Text, got {type(instance)}.")
        return instance


def load_statistic(instance: C, language: str) -> C:
    for aspect in LINGUISTIC_ASPECTS:
        feature_lang_suffix = "ENGLISH" if language == "en" else "SWEDISH"
        features = getattr(aspect, f"{feature_lang_suffix}_FEATURES")
        data = get_features_data(instance, aspect.ASPECT, features)
        setattr(instance, aspect.ASPECT, data)
    return instance


def get_features_data(instance: C, aspect: str, features: F) -> Dict[str, Feature]:
    data: Dict[str, Feature] = OrderedDict()
    for feature_name, func, attr_func, kwarg_list, attribute_kwargs in features:
        if isinstance(instance, Sentence):
            kwargs = parse_args(kwarg_list, getattr, instance)
            data[feature_name] = Feature(scalar=func(**kwargs))
        else:
            blocks = getattr(instance, instance.elements)
            kwargs = parse_args(kwarg_list, attr_func, blocks, **attribute_kwargs)
            scalar_list = [getattr(block, aspect)[feature_name].scalar for block in blocks]
            data[feature_name] = Feature(
                scalar=func(**kwargs), mean=mean(scalar_list), median=median(scalar_list)
            )
    return data # setup for token property after computation for sentence
