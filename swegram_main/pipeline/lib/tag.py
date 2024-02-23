"""Module of pos tagging
"""
import codecs
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from swegram_main.lib.utils import AnnotationError, change_suffix, cut, write
from swegram_main.config import EFSELAB_DIR, EFSELAB, UDPIPE, UDPIPE_MODEL
from tools.efselab import tagger  # pylint: disable=import-error, wrong-import-order


EFSELAB_MODEL = os.path.join(EFSELAB_DIR, "swe-pipeline")
UD_TAGGER_MODEL = os.path.join(EFSELAB_MODEL, "suc-ud.bin")
PARSING_MODEL = os.path.join(EFSELAB_MODEL, "old-swe-ud")
MALT = os.path.join(EFSELAB_MODEL, "maltparser-1.9.0/maltparser-1.9.0.jar")


class TaggingError(Exception):
    """Tagging Error"""


def write_tagged_conll(filepath: Path, tagged_path: Optional[Path] = None) -> None:  # pylint: disable=too-many-locals
    """Align the order of columns from .tag and convert it into .tag.conll
    which makes it possible to be parsed from efselab.
    
    Expected columns in .tag.conll
    token_index token lemma ud_tag suc_tag 
    filepath format
    word, suc_tag, ud_tag, lemma
    Återupptagande	NN|NEU|SIN|IND|NOM	NOUN	återupptagande
    """
    ud_tagger = tagger.UDTagger(UD_TAGGER_MODEL)
    # ud_tags_list is not extracted directly from .tag file
    # Instead, ud_tags_list is generated from ud_tagger    
    words, lemmas, ud_tags_list, suc_tags_list = [], [], [], []
    if not tagged_path:
        tagged_path = filepath.parent.joinpath(f"{filepath.stem}{os.path.extsep}tag")
    with tempfile.NamedTemporaryFile() as tmp_file:
        with codecs.open(tmp_file.name, mode="w", encoding="utf-8") as output_file:
            with codecs.open(filepath, mode="r", encoding="utf-8") as input_file:
                try:  # pylint: disable=too-many-try-statements
                    line = input_file.readline()
                    while line:
                        if line.strip() and not line.strip().startswith("#"):
                            word, suc_tag, _, lemma = line.strip().split("\t")
                            words.append(word)
                            lemmas.append(lemma)
                            suc_tags_list.append(suc_tag)
                        elif not line.strip() and words:
                            ud_tags_list = ud_tagger.tag(words, lemmas, suc_tags_list)
                            for index, (word, lemma, ud_tags, suc_tags) in enumerate(
                                zip(words, lemmas, ud_tags_list, suc_tags_list), 1
                            ):
                                ud_tag, ud_features = ud_tags.split("|", maxsplit=1)
                                output_file.write(
                                    "\t".join([str(index), word, lemma, ud_tag, suc_tags, ud_features]) + "\n"
                                )
                            output_file.write("\n")
                            words, lemmas, ud_tags_list, suc_tags_list = [], [], [], []
                        line = input_file.readline()

                except Exception as err:
                    raise TaggingError(
                        f"{err} Please check the format in tag file: {filepath}"
                        "The correct format is\n"
                        "<word>\t<suc_tag>\t<ud_tag>\t<lemma>"
                    ) from err
        shutil.copy(tmp_file.name, tagged_path)


def restore_en_original_norm_line(line: str) -> str:
    index, _, norm, *columns = line.split("\t")
    return "\t".join([index, norm, "_", *columns])


def restore_en_norm_file(filepath: Path) -> None:
    cut(restore_en_original_norm_line, filepath)


def tag(tagger_model: str, filepath: Path) -> None:
    try:
        if tagger_model.lower() == "efselab":
            subprocess.run(
                f"python3 {EFSELAB} --lemmatized --tagged --skip-tokenization " \
                f"-o {filepath.parent} {filepath}".split(), check=True
            )
            write_tagged_conll(change_suffix(filepath, "tag"))

        elif tagger_model.lower() == "udpipe":
            if filepath.suffix == ".spell":
                restore_en_norm_file(filepath)
            response = subprocess.run(
                f"{UDPIPE} --tag --input=conllu {UDPIPE_MODEL} {filepath}".split(),
                capture_output=True, check=False
            )
            if response.returncode != 0:
                raise AnnotationError(response.stderr.decode())
            write(
                filepath=filepath.parent.joinpath(os.path.extsep.join([filepath.stem, "tag"])),
                context=response.stdout.decode()
            )

    except Exception as err:
        raise AnnotationError(f"Failed to tokenize, {err}") from err
