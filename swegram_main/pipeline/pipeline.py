"""Module of pipeline


Unclear how compound check performs
"""

import os
import shutil

from pathlib import Path
from shutil import SameFileError
from typing import Optional
from swegram_main.data.texts import TextDirectory as TD
from swegram_main.pipeline.preprocess import preprocess
from swegram_main.pipeline.postprocess import aggregate_conlls, save
from swegram_main.pipeline.postprocess import postprocess as _postprocess
from swegram_main.pipeline.lib.normalize import normalize as normalize_
from swegram_main.pipeline.lib.parse import parse as parse_
from swegram_main.pipeline.lib.tokenize import tokenize as tokenize_
from swegram_main.pipeline.lib.tag import tag as tag_
from swegram_main.lib.logger import get_logger


logger = get_logger(__name__)


class PipelineError(Exception):
    """Pipeline Error"""


class Pipeline:

    default_output_dir = "output"

    def __init__(
        self, input_path: Path, output_dir: Optional[Path] = None, language: str = "sv"
    ) -> None:
        if not input_path.exists():
            raise FileNotFoundError(input_path)

        self.model = "efselab" if language == "sv" else "udpipe"
        self.input_path = input_path
        self.customized_output_dir = output_dir
        if self.customized_output_dir:
            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = self.input_path.absolute().parent.joinpath(self.default_output_dir)
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
            os.mkdir(str(self.output_dir))

        try:
            shutil.copy(self.input_path, self.output_dir)
        except SameFileError:
            pass

        self._preprocess()
        logger.debug(f"Working Directory: {self.output_dir}")

    def tokenize(self) -> None:
        for text in self.texts:
            if not text.tok.exists():
                tokenize(self.model, text)

    def normalize(self) -> None:
        normalizer = "histnorm_en" if self.model in {"histnorm_en", "udpipe"} else "histnorm_sv"
        for text in self.texts:
            if not text.spell.exists():
                normalize(normalizer, text)

    def tag(self) -> None:
        for text in self.texts:
            if not text.tag.exists():
                tag(self.model, text)

    def parse(self) -> None:
        for text in self.texts:
            if not text.conll.exists():
                parse(self.model, text)

    def _preprocess(self) -> None:
        self.texts = preprocess(self.input_path, self.output_dir, self.model)
        self.output_dir.joinpath(self.input_path.name).unlink(missing_ok=True)

    def postprocess(self, save_as: str = "txt", aggregate: bool = False) -> None:
        """
        if normalized: append original tokens in the list
        else: append normalized tokens in the list

        if efselab: split suc_tags into suc_tag and ufeats
        if not conll, convert to .conll
        """
        cache_save_as = save_as if not aggregate else "txt"
        normalization_tags, annotation_tags = [], []

        for text in self.texts:
            normalized, annotated = _postprocess(text, self.model, cache_save_as)
            normalization_tags.append(normalized)
            annotation_tags.append(annotated)

        if len(set(normalization_tags)) != 1:
            if normalization_tags:
                raise PipelineError(f"Inconsistent normalization across texts: {normalization_tags}")
            raise PipelineError("Missing annotated texts")
        if len(set(annotation_tags)) != 1:
            if annotation_tags:
                raise PipelineError(f"Inconsistent annotation phases across texts: {annotation_tags}")

        if aggregate:
            conll_filename = aggregate_conlls([text.conll for text in self.texts])
            if save_as != "txt":
                save(save_as, Path(conll_filename), self.model, normalization_tags[0], annotation_tags[0])

    def run(self, action: str, post_action: bool = True) -> None:
        if action == "tokenize":
            self.tokenize()
        elif action == "normalize":
            self.normalize()
        elif action == "tag":
            self.tag()
        elif action == "parse":
            self.parse()
        else:
            raise PipelineError(f"{action} is not valid. Choose tokenize, normalize, tag or parse")
        if post_action:
            self.postprocess()

    def load(self):
        """Extract the data and load into database"""


def tokenize(tokenizer: str, text: TD) -> None:
    tokenize_(tokenizer, text.filepath)    


def normalize(normalizer: str, text: TD) -> None:
    if not text.tok.exists():
        if normalizer.lower() == "histnorm_sv":
            tokenize_("efselab", text.filepath)
        elif normalizer.lower() == "histnorm_en":
            tokenize_("udpipe", text.filepath)
        else:
            raise PipelineError(f"Unknown normalizer: {normalizer}.")
    normalize_(normalizer, text.tok)
    # The generated norms are used to tag and parse
    text.tag.unlink(missing_ok=True)
    text.conll.unlink(missing_ok=True)


def tag(tagger: str, text: TD) -> None:
    if not text.tok.exists() and not text.spell.exists():
        tokenize_(tagger, text.filepath)
    if text.spell.exists():
        # workaround:
        # in case the uploaded normalized texts
        if not text.tok.exists():
            shutil.copy(text.spell, text.tok)
        tag_(tagger, text.spell)
    else:
        tag_(tagger, text.tok)


def parse(parser: str, text: TD) -> None:
    if not text.tag.exists():
        tag(parser, text)
    parse_(parser, text.tag)
