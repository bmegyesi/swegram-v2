from pathlib import Path
from typing import Dict, List, TypeVar

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.lib.utils import read_conll_file, get_content_md5
from swegram_main.statistics.statistic import Statistic

ST = TypeVar("ST", bound=List[str])  # Sentence Line Type
PT = TypeVar("PT", bound=List[List[str]]) # Paragraph Line Type
TT = TypeVar("TT", bound=List[List[List[str]]]) # Text Line Type


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


@Statistic
def load_sentence(text_id: str, lines: ST, language: str) -> Sentence:
    """Load sentence from conll text"""
    return Sentence(text_id=text_id, language=language, tokens=[load_token(line, language) for line in lines])


@Statistic
def load_paragraph(text_id: str, lines: PT, language: str) -> Paragraph:
    """Load paragraph from conll text"""
    return Paragraph(text_id=text_id, language=language, sentences=[load_sentence(text_id, s, language) for s in lines])


@Statistic
def load_text(text: TT, labels: Dict[str, str], language: str, filename: Path) -> Text:
    """Load text from conll text"""
    # p: paragraph, s: sentence, t: token
    text_id: str = get_content_md5("".join([t for p in text for s in p for t in s]).encode())
    paragraphs: List[Paragraph] = [load_paragraph(text_id, p, language) for p in text]
    return Text(paragraphs=paragraphs, text_id=text_id, language=language, filename=filename, labels=labels)


def load_file(input_file: Path, language: str) -> List[Text]:
    """Load texts from conll file"""
    return [load_text(text, labels, language, input_file) for text, labels in read_conll_file(input_file)]

sv = "tests/resources/10-sv.conll"
texts = load_file(Path(sv), "sv")
t1 = texts[0]
