"""Model of statistic.py
Create a decorator to append statistic e.g. Text instance

"""
from collections import OrderedDict
from typing import TypeVar
from swegram_main.lib.utils import mean, median, parse_args
from swegram_main.data.features import Feature
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.data.sentences import Sentence
from swegram_main.statistics.features.general import CountFeatures as CF
from swegram_main.statistics.features.lexical import LexicalFeatures as LF
from swegram_main.statistics.features.morph import MorphFeatures as MF
from swegram_main.statistics.features.readability import ReadabilityFeatures as RF
from swegram_main.statistics.features.syntactic import SyntacticFeatures as SF


U = TypeVar("U", Sentence, Paragraph, Text)


LINGUISTIC_ASPECTS = [RF, MF, LF, SF]  # CF is loaded separately


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
            raise Exception("Unknown working language for statistics.")

        if isinstance(instance, Sentence):
            instance = CF().load_instance(instance, language)
            instance = load_statistic(instance, language)
        elif isinstance(instance, Paragraph):
            instance = CF().load_instance(instance, language)
            instance = load_statistic(instance, language)
        elif isinstance(instance, Text):
            instance = CF().load_instance(instance, language)
            instance = load_statistic(instance, language)
        else:
            raise Exception(f"Unknown instance type, excepted to get Sentence, Paragraph, Text, got {type(instance)}.")
        return instance


def load_statistic(instance: U, language: str) -> U:
    for aspect in LINGUISTIC_ASPECTS:
        feature_lang_suffix = "ENGLISH" if language == "en" else "SWEDISH"
        features = getattr(aspect, f"{feature_lang_suffix}_FEATURES")
        data = get_features_data(instance, aspect.ASPECT, features)
        setattr(instance, aspect.ASPECT, data)
    return instance


def set_features_for_aspects(instance, level):
    for aspect in LINGUISTIC_ASPECTS:
        instance = get_features_data(instance, aspect, level)


def get_features_data(instance, aspect, features):
    data = OrderedDict()
    for feature_name, func, attr_func, kwarg_list, attribute_kwargs in features:
        if isinstance(instance, Sentence):
            kwargs = parse_args(kwarg_list, getattr, instance)
            data[feature_name] = Feature(scalar=func(**kwargs))  # data need to be fixed with aspect
        else:
            blocks = getattr(instance, instance.elements)
            kwargs = parse_args(kwarg_list, attr_func, blocks, **attribute_kwargs)
            scalar_list = [
                getattr(block, aspect)[feature_name].scalar for block in blocks
            ] # same for morph here
            data[feature_name] = Feature(
                scalar=func(**kwargs), mean=mean(scalar_list), median=median(scalar_list)
            )
    return data # setup for token property after computation for sentence
