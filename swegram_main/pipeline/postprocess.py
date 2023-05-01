"""Finalize the conll file after annotation

"""
import os
import shutil
from pathlib import Path
from typing import Iterator, Optional

from swegram_main.data.texts import TextDirectory as TD
from swegram_main.lib.utils import cut, read, change_suffix


def postprocess(text: TD, model: str) -> None:
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
        raise FileNotFoundError(f"No annotated files detected for {text.filepath}")


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
