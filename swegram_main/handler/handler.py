import os
from pathlib import Path
from typing import Dict, List, TypeVar, Optional

from swegram_main.data.metadata import convert_labels_to_list
from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text, Corpus
from swegram_main.lib.utils import read_conll_file, get_content_md5
from swegram_main.statistics.statistic import StatisticLoading


ST = TypeVar("ST", bound=List[str])  # Sentence Line Type
PT = TypeVar("PT", bound=List[List[str]]) # Paragraph Line Type
TT = TypeVar("TT", bound=List[List[List[str]]]) # Text Line Type


class InputError(Exception):
    """Input Error"""


def _load_token(text_index: str, token_index: str, form: str, norm: str, lemma: str,  # pylint: disable=too-many-arguments
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
def load_sentence(text_id: str, lines: ST, language: str, parsed: bool = True) -> Sentence:
    """Load sentence from conll text"""
    return Sentence(text_id=text_id, language=language, tokens=[load_token(line, language) for line in lines])


@StatisticLoading
def load_paragraph(text_id: str, lines: PT, language: str, parsed: bool = True) -> Paragraph:
    """Load paragraph from conll text"""
    return Paragraph(
        text_id=text_id, language=language, sentences=[load_sentence(text_id, s, language, parsed=parsed) for s in lines]
    )


@StatisticLoading
def load_text(text: TT, labels: Dict[str, str], language: str, filename: Path, parsed: bool = True) -> Text:
    """Load text from conll text"""
    # p: paragraph, s: sentence, t: token
    text_id: str = get_content_md5("".join([t for p in text for s in p for t in s]).encode())
    paragraphs: List[Paragraph] = [load_paragraph(text_id, p, language, parsed=parsed) for p in text]
    return Text(paragraphs=paragraphs, text_id=text_id, language=language, filename=filename, labels=labels)


def load_file(
    input_file: Path, language: str, include_tags: List[str], exclude_tags: List[str], parsed: bool = True
) -> List[Text]:
    """Load texts from conll file"""
    return [
        load_text(text, labels, language, input_file, parsed=parsed)
        for text, labels in read_conll_file(input_file)
        if is_text_included(labels, include_tags, exclude_tags)
    ]


def load_dir(
    input_dir: Path, language: str, include_tags: List[str], exclude_tags: List[str], parsed: bool = True
) -> List[Text]:
    """Load texts from one directory containing conll file"""
    conll_files = [input_dir.joinpath(filename) for filename in os.listdir(input_dir) if filename.endswith(".conll")]
    return [
        text for conll_file in conll_files
        for text in load_file(conll_file, language, include_tags, exclude_tags, parsed)
    ]


@StatisticLoading
def load(
    input_path: Path, language: str,
    include_tags: Optional[List[str]] = None, exclude_tags: Optional[List[str]] = None
) -> List[Text]:

    include_tags = include_tags or []
    exclude_tags = exclude_tags or []

    if input_path.is_dir():
        texts = load_dir(input_path, language, include_tags, exclude_tags)
        if not texts:
            raise InputError(f"Input directory {input_path} doesn't contain any conll files")
    elif input_path.is_file():
        if input_path.suffix != ".conll":
            raise InputError(f"Only conll file valid, got {input_path.suffix.lstrip('.')}")
        texts = load_file(input_path, language, include_tags, exclude_tags)
    else:
        raise InputError(f"Invalid input path: {input_path}")
    return Corpus(texts=texts, language=language)


def is_text_included(labels: Optional[Dict[str, str]], include_tags: List[str], exclude_tags: List[str]) -> bool:
    labels = labels or {}
    label_list = convert_labels_to_list(labels)
    if include_tags and not set(include_tags).intersection(label_list):
        return False
    if exclude_tags and set(exclude_tags).intersection(label_list):
        return False
    return True


def select_texts_by_meta(texts: List[Text], include_tags: List[str], exclude_tags: List[str]) -> List[Text]:
    """Filter first with include tags, and then exclude tags"""
    if include_tags:
        texts = [text for text in texts if set(text.metadata).intersection(include_tags)]
    if exclude_tags:
        texts = [text for text in texts if not set(text.metadata).intersection(exclude_tags)]
    return texts
