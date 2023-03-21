"""Module of pipeline


Unclear how compound check performs
"""
import logging
import os
import shutil
import tempfile

from pathlib import Path
from typing import Dict, Optional, Iterator

from swegram_main.pipeline.checker import check_text
from swegram_main.pipeline.preprocess import FileContent
from swegram_main.pipeline.lib.normalize import normalize as normalize_
from swegram_main.pipeline.lib.parse import parse as parse_
from swegram_main.pipeline.lib.tokenize import tokenize as tokenize_
from swegram_main.pipeline.lib.tag import tag as tag_
from swegram_main.lib.utils import cut, read, change_suffix


class PipelineError(Exception):
    """Pipeline Error"""


class StateError(Exception):
    """State error"""


class RestoreFileError(Exception):
    """Restore file error"""


class Text:

    def __init__(self, filepath: Path, meta: Optional[Dict[str, str]] = None) -> None:
        self.filepath = filepath
        _filename = lambda suffix: change_suffix(filepath, suffix)
        self.tok = _filename("tok")
        self.spell = _filename("spell")
        self.tag = _filename("tag")
        self.conll = _filename("conll")
        self.meta = meta

class State:
    """The state of annotation"""

    state_dict = {
        "tokenized": 0,
        "normalized": 1,
        "tagged": 2,
        "parsed": 3
    }

    def __init__(self, state) -> None:
        self.state = state.lower()
        if self.state not in self.state_dict:
            raise StateError(f"Unknown state: {self.state}. Valid states are {''.join(self.state_dict.keys())}")

    def __gt__(self, state1) -> bool:
        return self.state_dict[self.state] > self.state_dict[state1.state]

    def __ge__(self, state1) -> bool:
        return self.state_dict[self.state] >= self.state_dict[state1.state]

    def __le__(self, state1) -> bool:
        return self.state_dict[self.state] <= self.state_dict[state1.state]

    def __lt__(self, state1) -> bool:
        return self.state_dict[self.state] < self.state_dict[state1.state]

    def __eq__(self, state1) -> bool:
        return self.state == state1.state


class Pipeline:

    def __init__(self, filepath: Path, to_update: bool = False, output_dir: Optional[Path] = None) -> None:
        if not filepath.exists():
            raise FileNotFoundError(filepath)
        if output_dir:
            self.dir = output_dir
        else:
            tempdir = tempfile.TemporaryDirectory()
            self.dir = tempdir.name
        self.filepath = filepath
        shutil.copy(filepath, self.dir)

        self.texts = []
        self.text_index = 0
        self.preprocess()

    def _not_empty_text(self, text: Text) -> bool:
        if os.path.getsize(text.filepath) == 0:
            return False
        if text.meta:
            logging.debug(f"Empty text {text.filepath} contains metadata {text.meta}")
        return True

    def preprocess(self):
        try:
            file_content = FileContent(self.filepath).get()
            meta = None
            component = next(file_content)
            while True:
                text_path = Path(os.path.join(self.dir, f"{self.filepath.stem}_{str(self.text_index)}.txt"))
                text = Text(filepath=text_path, meta=meta)
                with open(text.filepath, "w") as input_file:
                    while True:
                        if isinstance(component, str):
                            input_file.write(component)
                        elif isinstance(component, dict):
                            break
                        else:
                            raise Exception(f"Unexpected parsed format of {component}: {type(component)}")
                        component = next(file_content)
                self.texts.append(text)
                self.text_index += 1
                meta = component
                component = next(file_content)
        except StopIteration:
            self.texts.append(text)
            self.texts = [text for text in self.texts if self._not_empty_text(text)]
            logging.info("Preprocessing done.")

    def tokenize(self, tokenizer: str) -> None:
        for text in self.texts:
            tokenize(tokenizer, text)

    def normalize(self, normalizer: str) -> None:
        for text in self.texts:
            normalize(normalizer, text)

    def tag(self, tagger: str) -> None:
        for text in self.texts:
            tag(tagger, text)

    def parse(self, parser: str) -> None:
        for text in self.texts:
            parse(parser, text)

    def _postprocess(self, model: str) -> None:
        """
        if normalized: append original tokens in the list
        else: append normalized tokens in the list
        
        if efselab: split suc_tags into suc_tag and ufeats

        if not conll, convert to .conll
        """
        for text in self.texts:
            text_postprocess(text, model)

    def run(self, model: str, action: str, post_action: bool = True) -> None:
        if action == "tokenize":
            self.tokenize(model)
        elif action == "normalize":
            # model = "udpipe" if model == "histnorm_en" else "efselab"
            self.normalize(model)
        elif action == "tag":
            self.tag(model)
        elif action == "parse":
            self.parse(model)
        else:
            raise PipelineError(f"{action} is not valid. Choose tokenize, normalize, tag or parse")
        if post_action:
            self._postprocess(model)

    def restore_and_run(self, model: str, from_: str, to_: str, check_text: bool = True) -> None:
        """Given the partially annotated text, restore the annotated text to "from_" phase
        and continue annotation to "to_" phase in the annotation pipeline

        :param model: the applied model. It can be efselab, udpipe, histnorm_en, histnorm_sv.
        :type model: str
        :param from_: the phase of annotation. One of the following (tokenized, normalized, tagged, parsed)
        :type from_: str
        :param to_: the phase of annotation. One of the following (tokenized, normalized, tagged, parsed)
        :type to_: str
        :param check_text: if needed to check if text meets the requirements in form of conll format, defaults to True
        :type check_text: bool, optional
        """
        for text in self.texts:
            annotate(text, from_, to_, model, check_text)

    def load(self):
        """Extract the data and load into database"""


def text_postprocess(text: Text, model: str):
    if text.spell.exists():
        tokens = read(text.tok)
        normalized = True
    else:
        tokens = None
        normalized = False

    if text.conll.exists():
        if model.lower() == "efselab":
            postprocess_helper(model, text.conll, True, normalized, tokens)
        else:
            postprocess_helper(model, text.conll, False, normalized, tokens)
    elif text.tag.exists():
        if model.lower() == "efselab":
            postprocess_helper(model, text.tag, True, normalized, tokens)
        else:
            postprocess_helper(model, text.tag, False, normalized, tokens)
    elif text.tok.exists():
        if model.lower() in ["efselab", "histnorm_sv"]:
            postprocess_helper(model, text.tok, True, normalized, tokens)
        else:
            postprocess_helper(model, text.tok, False, normalized, tokens)
    else:
        raise PipelineError(f"No annotated files detected for {text.filepath}")


def postprocess_helper(
    model: str, filepath: Path, split_suc_tags: bool, normalized: bool,
    tokens: Optional[Iterator] = None
) -> None:
    copy_to_conll = True
    file_type = filepath.suffix.lstrip(os.path.extsep)
    if file_type == "conll":
        copy_to_conll = False
        merge_func = lambda line: _post_file(line, split_suc_tags, normalized, False, model, tokens)
    elif file_type == "tag":
        merge_func = lambda line: _post_file(line, split_suc_tags, normalized, True, model, tokens)
    elif file_type == "tok":
        merge_func = lambda line: _post_tok_file(line, split_suc_tags, normalized, model, tokens)
    if file_type == "tok" and model.lower() in ["histnorm_sv", "efselab"]:
        cut(merge_func, filepath, append_token_index=True, append_text_index=True)
    else:
        cut(merge_func, filepath, append_text_index=True)
    if copy_to_conll:
        shutil.copy(filepath, change_suffix(filepath, "conll"))


def update(to_: str, filepath: Path, model: str, force_normalize: Optional[bool] = None) -> None:
    """Given a partial annotated text and continue annotating when needed.
    With force_normalize, the text will only keep the tokenization and do/redo normalization
    """
    # process in a temp dir
    temp_dir = tempfile.TemporaryDirectory()
    workspace = Path(temp_dir.name)
    text = Text(workspace.joinpath(filepath.name))

    if force_normalize is True:
        restore("tokenized", filepath, workspace, model, False)
        check_text(model, read(filepath))
        normalizer = "histnorm_sv" if model.lower() == "efselab" else "histnorm_en"
        normalize_(normalizer, change_suffix(filepath, "tok"))
        annotate(text, "normalized", to_, model)

    else:
        # check the format given the file
        normalized, tagged, parsed = check_text(model, read(filepath))
        if parsed:
            from_ = "parsed"
        elif tagged:
            from_ = "tagged"
        elif normalized:
            from_ = "normalized"
        else:
            from_ = "tokenized"
        restore(from_, filepath, workspace, model, normalized)
        annotate(text, from_, to_, model)
    shutil.copy(workspace.joinpath(f"{filepath.stem}{os.path.extsep}conll"), change_suffix(filepath, "conll"))


def tokenize(tokenizer: str, text: Text) -> None:
    tokenize_(tokenizer, text.filepath)    


def normalize(normalizer: str, text: Text) -> None:
    if not text.tok.exists():
        if normalizer.lower() == "histnorm_sv":
            tokenize_("efselab", text.filepath)
        elif normalizer.lower() == "histnorm_en":
            tokenize_("udpipe", text.filepath)
        else:
            raise PipelineError(f"Unknown normalizer: {normalizer}.")
    normalize_(normalizer, text.tok)


def tag(tagger: str, text: Text) -> None:
    if not text.tok.exists() and not text.spell.exists():
        tokenize_(tagger, text.filepath)
    if text.spell.exists():
        tag_(tagger, text.spell)
    else:
        tag_(tagger, text.tok)


def parse(parser: str, text: Text) -> None:
    if not text.tag.exists():
        tag(parser, text)
    parse_(parser, text.tag)


def run(text: Text, to_: str, model: str) -> None:
    if to_ == "tokenized":
        tokenize(model, text)
    elif to_ == "normalized":
        normalize(model, text)
    elif to_ == "tagged":
        tag(model, text)
    elif to_ == "parsed":
        parse(model, text)
    else:
        PipelineError(f"Annotated to state {to_} is not valid. Choose tokenized, normalizekd, tagged or parsed")


def annotate(text: Text, from_: str, to_: str, model: str, check_text: bool = False):
    """Given text object, annotate the target text from state A to B with model M
    """
    if check_text:
        check_text(model, read(text.conll))
    if State(from_) < State(to_):
        run(text, to_, model)
        text_postprocess(text, model)


def restore_tokenized_line(line: str, model: str) -> str:
    if model.lower() == "efselab":
        _, _, token, *_ = line.split("\t")
        return f"{token}\n"
    elif model.lower() == "udpipe":
        _, index, token, _, lemma, *columns = line.split("\t")
        return "\t".join([index, token, lemma, *columns])
    else:
        raise RestoreFileError(f"Failed to parse tokenized line: {line}")
    

def restore_normalized_line(line: str, model: str) -> str:
    if model.lower() == "efselab":
        _, _, _, norm, *_ = line.split("\t")
        return f"{norm}\n"
    elif model.lower() == "udpipe":
        _, index, token, norm, _, *columns = line.split("\t")
        return "\t".join([index, token, norm, *columns])
    else:
        raise RestoreFileError(f"Failed to parse normalized line: {line}")


def restore_tagged_line(line: str, model: str, normalized: bool) -> str:
    if model.lower() == "efselab":
        _, index, token, norm, lemma, ud_tag, suc_tag, ud_features, suc_features, *_ = line.split("\t")
        if suc_features != "_":
            suc_column = f"{suc_tag}|{suc_features}"
        else:
            suc_column = suc_tag
        if normalized:
            return "\t".join([index, norm, lemma, ud_tag, suc_column, ud_features]) + "\n"
        else:
            return "\t".join([index, token, lemma, ud_tag, suc_column, ud_features]) + "\n"
    elif model.lower() == "udpipe":
        if normalized:
            _, index, _, *columns = line.split("\t")
            return "\t".join([index, *columns])
        else:
            _, index, token, _, *columns = line.split("\t")
            return "\t".join([index, token, *columns])
    else:
        raise PipelineError(f"Unknow model to restore tagged line: {model}")


def restore(
    from_: str, filepath: Path, workspace: Path, model: str = "efselab",
    normalized: Optional[bool] = None
) -> None:
    """Restore the uploaded annotated text into a format that allows pipeline process further
    """
    restore_tokenized_line_helper = lambda line: restore_tokenized_line(line, model)
    restore_normalized_line_helper = lambda line: restore_normalized_line(line, model)
    if from_ == "tokenized":
        cut(restore_tokenized_line_helper, filepath, output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok"))

    elif from_ == "normalized":
        cut(restore_tokenized_line_helper, filepath, output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok"))
        cut(restore_normalized_line_helper, filepath, output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}spell"))

    elif from_ == "tagged":
        if normalized:
            cut(restore_tokenized_line_helper, filepath, output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok"))
        cut(
            lambda line: restore_tagged_line(line, model, normalized),
            filepath,
            output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tag")
        )
        
    else:
        raise Pipeline(f"Unknown state for annotation: {from_}")


def _get_next_token(tokens: Iterator, model: str) -> str:
    token = next(tokens)
    if model.lower() in ["udpipe", "histnorm_en"]:
        while not token.strip() or token.startswith("#"):
            token = next(tokens)
        return token.strip('\n').split('\t')[1]
    else:
        while not token.strip():
            token = next(tokens)
        return token.strip('\n')


def _post_file(
    line: str, split_suc_tags: bool, normalized: bool, from_tag: bool,
    model: str, tokens: Optional[Iterator] = None
) -> str:
    if split_suc_tags:
        index, word, lemma, ud_tag, suc_tags, ud_features, *rest_columns = line.split("\t")
        if "|" in suc_tags:
            suc_tag, suc_features = suc_tags.split("|", maxsplit=1)
        else:
            suc_tag, suc_features = suc_tags, "_"
        if from_tag:
            rest_columns.extend(["_"] * 3 + ["_\n"])
        if normalized:
            return "\t".join([
                index, _get_next_token(tokens, model), word, lemma, ud_tag,
                suc_tag, ud_features.strip(), suc_features, *rest_columns
            ])
        else:
            return "\t".join([
                index, word, "_", lemma, ud_tag, suc_tag, ud_features.strip(), suc_features, *rest_columns
            ])
    else:
        index, word, *rest_columns = line.split("\t")
        if normalized:
            return "\t".join([index, _get_next_token(tokens, model), word, *rest_columns])
        else:
            return "\t".join([index, word, "_", *rest_columns])


def _post_tok_file(
    line: str, split_suc_tags: bool, normalized: bool,
    model: Optional[str] = None, tokens: Optional[Iterator] = None
) -> str:
    if model.lower() in ["efselab", "histnorm_sv"]:
        word, *rest_columns = line.split("\t")
        if split_suc_tags:
            rest_columns.extend(["_"] * 8 + ["_\n"])

        if normalized:
            return "\t".join([_get_next_token(tokens, model).strip(), word.strip(), *rest_columns])
        else:
            return "\t".join([word.strip(), "_", *rest_columns])
    else:
        index, word, *rest_columns = line.split("\t")

        if normalized:
            return "\t".join([index, _get_next_token(tokens, model).strip(), word.strip(), *rest_columns])
        else:
            return "\t".join([index, word.strip(), "_", *rest_columns])
