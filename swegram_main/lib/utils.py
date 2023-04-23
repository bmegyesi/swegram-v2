import codecs
import logging
import os
import shutil
import tempfile
from typing import Callable, Dict, Generator, Iterator, List, Optional, TypeVar, Tuple, Union
from hashlib import md5
from pathlib import Path

from swegram_main.data.metadata import parse_metadata
from swegram_main.lib.converter import Converter
from swegram_main.lib.logger import get_logger


T = TypeVar("T", bound=List[Tuple[List[List[List[str]]], Dict[str, str]]])
FT = TypeVar("FT", bound=Iterator[Union[Dict[str, str], str]])
logger = get_logger(__name__)


class MetaFormatError(Exception):
    """Meta format error"""


class ConllFormatError(Exception):
    """conll format error"""


class AnnotationError(Exception):
    """Annotation error"""


class FileContent:

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def _convert(self):
        yield from Converter(self.filepath).parse()

    def get(self) -> FT:
        for line in self._convert():
            if not line:
                continue
            metadata = parse_metadata(line)
            if metadata is None:
                yield line
            else:
                yield metadata


def get_md5(filepath: Path) -> str:
    """Get md5 value"""
    with codecs.open(filepath, "rb") as inputfile:
        return md5(inputfile.read()).hexdigest()


def get_conll_md5(filepath: Path) -> str:
    with open(filepath, "r") as input_file:
        lines = [line for line in input_file.readlines() if not line.startswith("#")]
        return md5("\n".join(lines).encode()).hexdigest()


def get_content_md5(content: str) -> str:
    return md5(content).hexdigest()


def get_size(filepath: Path) -> Optional[int]:
    """Get size"""
    if not os.path.exists(filepath):
        logging.debug(f"{filepath} does not exist.")
        return None
    return os.path.getsize(filepath)


def write(filepath: Path, context: str) -> None:
    """Write into file with context"""
    with codecs.open(filepath, mode="w", encoding="utf-8") as output_file:
        output_file.write(context)


def read(filepath: Path) -> Generator:
    """Read out file given arg into generator"""
    with codecs.open(filepath, mode="r", encoding="utf-8") as input_file:
        line = input_file.readline()
        while line:
            yield line
            line = input_file.readline()


def _initialize_conllu_reading(file_content: FT) -> Tuple[Union[None, Dict[str, str]], Union[str, Dict[str, str]]]:
    component = next(file_content)
    while True:
        # Skip blank lines in the beginning of the file content
        if isinstance(component, str):
            if not component.strip():
                component = next(file_content)
            else:
                return None, component
        elif isinstance(component, dict):
            return component, next(file_content)
        else:
            raise MetaFormatError(f"Invalid format, got {type(component)}:{component}")
    

def read_conll_file(input_path: Path) -> T:
    """Read conllu text"""
    texts: T = []
    paragraphs, sentences, sentence, = [], [], []
    file_content = FileContent(input_path).get()

    def _append_paragraph() -> None:
        if sentences and sentence:
            sentences.append(sentence)
        elif sentence:
            sentences.append(sentence)
        if sentences:
            paragraphs.append(sentences)

    def _append_text(meta: Dict[str, str]) -> None:
        _append_paragraph()
        if paragraphs:
            texts.append((paragraphs, meta))
        elif meta:
            logger.warning(f"Medata data {meta}: text is empty")

    try:
        meta, component = _initialize_conllu_reading(file_content)
        while True:
            newline = 0
            while True:
                if isinstance(component, str):
                    if component == "\n":
                        newline += 1
                    elif component.startswith("#"):
                        pass
                    else:
                        if not newline:
                            sentence.append(component)
                        elif newline == 2:
                            _append_paragraph()
                            sentence = [component]
                            newline = 0
                        elif newline == 1:
                            if sentence:
                                sentences.append(sentence)
                                sentences, sentence = [], [component]
                                newline = 0
                        else:
                            raise ConllFormatError(f"Too many blank lines, max 2 newlines , but got {newline}")
                elif isinstance(component, dict):
                    _append_text(meta)
                    meta = component
                    paragraphs = []
                    break
                else:
                    raise MetaFormatError(f"Invalid format, got {type(component)}:{component}")
                component = next(file_content)
            component = next(file_content)

    except StopIteration:
        _append_text(meta)
    return texts


def cut(
    func: Callable, filepath: Path, output_path: Optional[Path] = None, append_token_index: bool = False,
    append_text_index: bool = False, *args, **kwargs
) -> None:
    """insertion in the annotation files"""
    lines = read(filepath)
    index = 0
    paragraph_index, sentence_index = 1, 1
    num_newlines = 0
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as output_file:
        try:
            while True:
                line = next(lines)
                if line.strip() and not line.strip().startswith("#"):
                    line = func(line)
                    if append_token_index:
                        if num_newlines > 0:
                            index = 1
                        else:
                            index += 1
                        line = "\t".join([str(index), line])
                            
                    if append_text_index:
                        if num_newlines > 1:
                            paragraph_index += 1
                            sentence_index = 1
                            num_newlines = 0
                        elif num_newlines == 1:
                            sentence_index += 1
                            num_newlines = 0
                        line = "\t".join([f"{paragraph_index}.{sentence_index}", line])
                    output_file.write(line)
                else:
                    output_file.write(line)
                    if line == "\n":
                        num_newlines += 1
        except StopIteration:
            output_file.flush()
            if output_path:
                shutil.copy(output_file.name, output_path)
            else:
                shutil.copy(output_file.name, filepath)


def change_suffix(filepath: Path, suffix: str) -> Path:
    return filepath.parent.joinpath(f"{filepath.stem}{os.path.extsep}{suffix}")
