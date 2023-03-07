from pathlib import Path
from typing import Dict, List, TypeVar

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.lib.utils import read_conllu, get_conllu_md5


ST = TypeVar("ST", bound=List[str])  # Sentence Line Type
PT = TypeVar("PT", bound=List[List[str]]) # Paragraph Line Type
TT = TypeVar("TT", bound=List[List[List[str]]]) # Text Line Type


def _load_token(text_index: str, token_index: str, form: str, norm: str, lemma: str,
    upos: str, xpos: str, feats: str, ufeats: str, head: str, deprel: str, deps: str, misc: str) -> Token:
    return Token(text_index=text_index, token_index=token_index, form=form, norm=norm, lemma=lemma,
    upos=upos, xpos=xpos, feats=feats, ufeats=ufeats, head=head, deprel=deprel, deps=deps, misc=misc)


def load_token(line: str) -> Token:
    """Load token"""
    args = line.strip().split("\t")
    if len(args) == 12:
        args.insert(8, None)
    return _load_token(*args)


def load_sentence(text_id: str, lines: ST) -> Sentence:
    """Load sentence from conllu text"""
    return Sentence(text_id=text_id, tokens=[load_token(line) for line in lines])


def load_paragraph(text_id: str, lines: PT) -> Paragraph:
    """Load paragraph from conllu text"""
    return Paragraph(text_id=text_id, sentences=[load_sentence(text_id, s) for s in lines])


def load_text(language: str, filename: Path, labels: Dict[str, str]) -> Text:
    """Load text from conllu text"""
    text_id: str = get_conllu_md5(filename)
    paragraphs: List[Paragraph] = [load_paragraph(text_id, p) for p in read_conllu(filename)]
    return Text(paragraphs=paragraphs, text_id=text_id, language=language, filename=filename, labels=labels)
