import codecs
import logging
import os
import shutil
import tempfile
from typing import Callable, Generator, List, Optional
from hashlib import md5
from pathlib import Path


class ConllFormatError(Exception):
    """conll format error"""


class AnnotationError(Exception):
    """Annotation error"""


def get_md5(filepath: Path) -> str:
    """Get md5 value"""
    with codecs.open(filepath, "rb") as inputfile:
        return md5(inputfile.read()).hexdigest()


def get_conllu_md5(filepath: Path) -> None:
    with open(filepath, "r") as input_file:
        lines = [line for line in input_file.readlines() if not line.startswith("#")]
        return md5("\n".join(lines).encode()).hexdigest()


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


def read_conllu(filepath: Path) -> List[List[List[str]]]:
    """Read conllu text"""
    with codecs.open(filepath, mode="r", encoding="utf-8") as input_file:
        paragraphs, sentences, sentence = [], [], []
        newline = 0
        line = input_file.readline()
        while line:
            if line == "\n":
                newline += 1
            elif line.startswith("#"):
                pass
            else:
                if not newline:
                    sentence.append(line)
                elif newline == 2:
                    if sentences:
                        if sentence:
                            sentences.append(sentence)
                        paragraphs.append(sentences)
                        sentences, sentence = [], [line]
                        newline = 0
                elif newline == 1:
                    if sentence:
                        sentences.append(sentence)
                        sentence = [line]
                        newline = 0
                else:
                    raise ConllFormatError(f"Too many blank lines, max 2 newlines, but got {newline}")
            line = input_file.readline()

        if sentence:
            sentences.append(sentence)
        if sentences:
            paragraphs.append(sentences)
        return paragraphs


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