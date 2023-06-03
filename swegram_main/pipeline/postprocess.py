"""Finalize the conll file after annotation

"""
import fileinput
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, List, Dict, Tuple

from swegram_main.config import (
    AGGREGATION_CONLLS, EMPTY_METADATA, JSON_CONLL_CORPUS_KEY, JSON_CONLL_METADATA_KEY, JSON_CONLL_TEXT_KEY
)
from swegram_main.data.metadata import parse_metadata, convert_labels_to_string
from swegram_main.data.texts import TextDirectory as TD
from swegram_main.lib.utils import change_suffix, cut, read, read_conll_file, XlsxAnnotationClient


class EmptyConllFile(Exception):
    """Empty Conll File"""


def postprocess(text: TD, model: str, save_as: str) -> Tuple[str, bool, str]:
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
        annotation = "parsed"
    elif text.tag.exists():
        if model.lower() == "efselab":
            postprocess_helper(model, text.tag, True, normalized, tokens)
        else:
            postprocess_helper(model, text.tag, False, normalized, tokens)
        annotation = "tagged"
    elif text.tok.exists():
        if model.lower() in {"efselab", "histnorm_sv"}:
            postprocess_helper(model, text.tok, True, normalized, tokens)
        else:
            postprocess_helper(model, text.tok, False, normalized, tokens)
        annotation = "tokenized"
    else:
        raise FileNotFoundError(f"No annotated files detected for {text.filepath}")

    if text.meta:
        insert_metadata(text.conll, text.meta)

    save(save_as, text.conll, model, normalized, annotation)
    return normalized, annotation


def insert_metadata(filepath: Path, metadata: Dict[str, str]) -> None:
    with fileinput.input(filepath, inplace=True) as input_file:
        for line in input_file:
            if input_file.isfirstline():
                print(convert_labels_to_string(metadata))
            print(line.strip())


def save(save_as: str, conll: Path, model: str, normalized: bool, annotation: str) -> None:
    language = "sv" if model.lower() in {"efselab", "histnorm_sv"} else "en"
    if save_as == "json":
        save_as_json(conll, model, language, normalized, annotation)
    elif save_as == "xlsx":
        save_as_xlsx(conll, model, language, normalized, annotation)
    elif save_as != "txt":
        raise TypeError(f"Only support txt, json, xlsx, but got {save_as} instead.")


def save_as_json(conll: Path, model: str, language: str, normalized: bool, annotation: str) -> None:
    """Save as json format"""
    json_object = json.dumps(
        {
            "Timestamp": str(datetime.now()), "Model": model, "Language": language,
            "Normalization": normalized, "Annotation": annotation,
            JSON_CONLL_CORPUS_KEY: [
                {JSON_CONLL_METADATA_KEY: labels, JSON_CONLL_TEXT_KEY: text} for text, labels in read_conll_file(conll)
            ]
        },
        indent=4
    )

    with open(change_suffix(conll, "json"), "w", encoding="utf-8") as output_file:
        output_file.write(json_object)


def save_as_xlsx(conll: Path, model: str, language: str, normalized: bool, annotation: str) -> None:
    """Save as xlsx format"""
    XlsxAnnotationClient(change_suffix(conll, "xlsx")).dump(conll, model, language, normalized, annotation)


def get_aggregate_filename(file_path: Path, basename: str) -> str:
    return os.path.join(os.path.abspath(os.path.dirname(file_path)), basename)


def get_conll(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as conll_file:
        lines = conll_file.readlines()
        while lines:
            first_line = lines.pop(0)
            if first_line.strip() and parse_metadata(first_line):
                return "".join([first_line, *lines])
            if first_line.strip():
                return "".join([f"{EMPTY_METADATA}\n", first_line, *lines])
        raise EmptyConllFile(f"File path: {file_path}")


def aggregate_conlls(file_paths: List[Path]) -> str:
    filename = get_aggregate_filename(file_paths[0], AGGREGATION_CONLLS)
    with open(filename, "w", encoding="utf-8") as output_file:
        for file_path in file_paths:
            output_file.write(get_conll(file_path))
    return filename


def postprocess_helper(
    model: str, filepath: Path, split_suc_tags: bool, normalized: bool,
    tokens: Optional[Iterator] = None
) -> None:
    copy_to_conll = True
    file_type = filepath.suffix.lstrip(os.path.extsep)
    if file_type == "conll":
        copy_to_conll = False
        def merge_func(line: str) -> str:
            return _post_file(line, split_suc_tags, normalized, False, model, tokens)
    elif file_type == "tag":
        def merge_func(line: str) -> str:
            return _post_file(line, split_suc_tags, normalized, True, model, tokens)
    elif file_type == "tok":
        def merge_func(line: str) -> str:
            return _post_tok_file(line, split_suc_tags, normalized, model, tokens)
    if file_type == "tok" and model.lower() in {"histnorm_sv", "efselab"}:
        cut(merge_func, filepath, append_token_index=True, append_text_index=True)
    else:
        cut(merge_func, filepath, append_text_index=True)
    if copy_to_conll:
        shutil.copy(filepath, change_suffix(filepath, "conll"))


def _get_next_token(tokens: Iterator, model: str) -> str:
    token = next(tokens)
    if model.lower() in {"udpipe", "histnorm_en"}:
        while not token.strip() or token.startswith("#"):
            token = next(tokens)
        return token.strip('\n').split('\t')[1]

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
        return "\t".join([
            index, word, "_", lemma, ud_tag, suc_tag, ud_features.strip(), suc_features, *rest_columns
        ])

    index, word, *rest_columns = line.split("\t")
    if normalized:
        return "\t".join([index, _get_next_token(tokens, model), word, *rest_columns])

    return "\t".join([index, word, "_", *rest_columns])


def _post_tok_file(
    line: str, split_suc_tags: bool, normalized: bool,
    model: Optional[str] = None, tokens: Optional[Iterator] = None
) -> str:
    if model.lower() in {"efselab", "histnorm_sv"}:
        word, *rest_columns = line.split("\t")
        if split_suc_tags:
            rest_columns.extend(["_"] * 8 + ["_\n"])

        if normalized:
            return "\t".join([_get_next_token(tokens, model).strip(), word.strip(), *rest_columns])
        return "\t".join([word.strip(), "_", *rest_columns])

    index, word, *rest_columns = line.split("\t")

    if normalized:
        return "\t".join([index, _get_next_token(tokens, model).strip(), word.strip(), *rest_columns])

    return "\t".join([index, word.strip(), "_", *rest_columns])
