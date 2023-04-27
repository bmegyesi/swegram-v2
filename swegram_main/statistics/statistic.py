"""Model of statistic.py
Create a decorator to append statistic e.g. Text instance

"""
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.statistics.features.general import CountFeatures as CF
from swegram_main.statistics.features.readability import ReadabilityFeatures as RF

class Statistic:

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
            instance.general = CF(instance.tokens, language)
            instance.readability = RF(instance.tokens, language, sentence=instance)
        elif isinstance(instance, Paragraph):
            instance.general = CF(instance.sentences, language)
            instance.readability = RF(instance.sentences, language)
        elif isinstance(instance, Text):
            instance.general = CF(instance.paragraphs, language)
            instance.readability = RF(instance.paragraphs, language)
        else:
            raise Exception(f"Unknown instance type, excepted to get Sentence, Paragraph, Text, got {type(instance)}.")
        return instance
