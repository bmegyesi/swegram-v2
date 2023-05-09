import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, TypeVar, Tuple, Optional

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.lib.utils import read_conll_file, get_content_md5
from swegram_main.statistics.statistic import StatisticLoading
from swegram_main.statistics.statistic_types import C


ST = TypeVar("ST", bound=List[str])  # Sentence Line Type
PT = TypeVar("PT", bound=List[List[str]]) # Paragraph Line Type
TT = TypeVar("TT", bound=List[List[List[str]]]) # Text Line Type
ASPECTS = ["general", "readability", "morph", "lexical", "syntactic"]


def _load_token(text_index: str, token_index: str, form: str, norm: str, lemma: str,
    upos: str, xpos: str, feats: str, ufeats: str, head: str, deprel: str, deps: str, misc: str) -> Token:
    return Token(text_index=text_index, token_index=token_index, form=form, norm=norm, lemma=lemma,
    upos=upos, xpos=xpos, feats=feats, ufeats=ufeats, head=head, deprel=deprel, deps=deps, misc=misc)


def load_token(line: str, language: str) -> Token:
    """Load token"""
    args = line.strip().split("\t")
    if language == "en":
        args.insert(8, None)
    return _load_token(*args)


@StatisticLoading
def load_sentence(text_id: str, lines: ST, language: str) -> Sentence:
    """Load sentence from conll text"""
    return Sentence(text_id=text_id, language=language, tokens=[load_token(line, language) for line in lines])


@StatisticLoading
def load_paragraph(text_id: str, lines: PT, language: str) -> Paragraph:
    """Load paragraph from conll text"""
    return Paragraph(text_id=text_id, language=language, sentences=[load_sentence(text_id, s, language) for s in lines])


@StatisticLoading
def load_text(text: TT, labels: Dict[str, str], language: str, filename: Path) -> Text:
    """Load text from conll text"""
    # p: paragraph, s: sentence, t: token
    text_id: str = get_content_md5("".join([t for p in text for s in p for t in s]).encode())
    paragraphs: List[Paragraph] = [load_paragraph(text_id, p, language) for p in text]
    return Text(paragraphs=paragraphs, text_id=text_id, language=language, filename=filename, labels=labels)


def load_file(input_file: Path, language: str) -> List[Text]:
    """Load texts from conll file"""
    return [load_text(text, labels, language, input_file) for text, labels in read_conll_file(input_file)]


def load_dir(input_dir: Path, language: str) -> List[Text]:
    """Load texts from one directory containing conll file"""
    conll_files = [input_dir.joinpath(filename) for filename in os.listdir(input_dir)] 
    return [text for conll_file in conll_files for text in load_file(conll_file, language)]


def c(v: Optional[str]) -> str:
    return v if v else ""


def format_aspect(features: OrderedDict) -> None:
    for key, v in features.items():
        print(f"{' ':>2}{key:>30}{'|':>4}{c(v.scalar):>10}{'|':>4}{c(v.mean):>10}{'|':>4}{c(v.median):>10}{'|':>4}")



def format_aspects(aspects: List[Tuple[str, str, OrderedDict]]) -> None:
    for aspect_name, reference, features in aspects:
        print(f"-"*78)
        print(f"Aspect:{aspect_name}    Reference: {reference}")
        format_aspect(features)
        print(f"-"*78)
        print()


def get_aspects(block: C, reference: str) -> List[Tuple[str, OrderedDict]]:
    aspects = []
    for aspect in ASPECTS:
        if aspect == "general":
            aspects.append((aspect, reference, block.general.data))
        elif aspect == "morph":
            try:
                for od in block.morph:
                    aspects.append((f"{aspect}-{od['name']}", reference, od["data"]))
            except Exception as err:
                import pdb; pdb.set_trace()
                print()
        else:
            aspects.append((aspect, reference, getattr(block, aspect)))
    return aspects
        

class Statistic:

    def __init__(self, input_path: Path, language: str, levels: List[str]):
        if input_path.is_dir():
            self.texts = load_dir(input_path, language)
            if not self.texts:
                raise Exception(f"Input directory {input_path} doesn't contain any conll files")
        elif input_path.is_file():
            if input_path.suffix != ".conll":
                raise Exception(f"Only conll file valid, got {input_path.suffix.lstrip('.')}")
            self.texts = load_dir(input_path, language)
        else:
            raise Exception(f"Invalid input path: {input_path}")

        self.levels = levels if levels else ["text"]

    def generate(self) -> None:
        for t_index, text in enumerate(self.texts, 1):
            if "text" in self.levels:
                format_aspects(get_aspects(text, f"text-{t_index}"))
            for p_index, paragraph in enumerate(text.paragraphs, 1):
                if "paragraph" in self.levels:
                    format_aspects(get_aspects(paragraph, f"paragraph-{t_index}-{p_index}"))
                for s_index, sentence in enumerate(paragraph.sentences, 1):
                    if "sentence" in self.levels:
                        format_aspects(get_aspects(sentence, f"sentence-{t_index}-{p_index}-{s_index}"))
