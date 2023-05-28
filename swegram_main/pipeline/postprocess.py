"""Finalize the conll file after annotation

"""
import json
import os
import shutil
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, List, Dict

from swegram_main.data.texts import TextDirectory as TD
from swegram_main.lib.utils import change_suffix, cut, read, read_conll_file, XlsxWriter


class XlsxAnnotationWriter(XlsxWriter):

    def __init__(self, output_path: Path) -> None:
        super().__init__(output_path)

    def load(self, conll: Path, language: str, normalized: bool, annotation: str):
        text, labels = read_conll_file(conll)[0]
        meta_sheet = self.wb["Sheet"]
        meta_sheet.title = "Annotation-metadata"
        meta_sheet["A1"] = "Swegram Annotation"
        metadata = OrderedDict({
            "Language": language,
            "Normalization": normalized,
            "Annotation": annotation,
            "Labels": labels
        })
        for row, (key, value) in enumerate(metadata.items(), 2):
            self.load_cell(meta_sheet, row, 1, key)
            self.load_cell(meta_sheet, row, 2, value)
        self.load_text(text)
        self.wb.save(filename=self.output_name)

    def load_text(self, text: List[List[List[str]]]) -> None:
        sheet = self.wb.create_sheet(title="content")
        row = 1
        for paragraph in text:
            for sentence in paragraph:
                for token in sentence:
                    fields = token.split("\t")
                    for col, field in enumerate(fields, 1):
                        self.load_cell(sheet, row, col, field)
                    row += 1
                row += 1
            row += 1


def postprocess(text: TD, model: str, save_as: str) -> None:
    if text.spell.exists():
        tokens = read(text.tok)
        normalized = True
    else:
        tokens = None
        normalized = False

    language = "sv" if model.lower() in ["efselab", "histnorm_sv"] else "en"

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
        if model.lower() in ["efselab", "histnorm_sv"]:
            postprocess_helper(model, text.tok, True, normalized, tokens)
        else:
            postprocess_helper(model, text.tok, False, normalized, tokens)
        annotation = "tokenized"
    else:
        raise FileNotFoundError(f"No annotated files detected for {text.filepath}")

    save(save_as, text.conll, language, normalized, annotation)


def save(save_as: str, conll: Path, language: str, normalized: bool, annotation: str) -> None:
    if save_as == "json":
        save_as_json(conll, language, normalized, annotation)
    elif save_as == "xlsx":
        save_as_xlsx(conll, language, normalized, annotation)
    elif save_as != "txt":
        raise TypeError(f"Only support txt, json, xlsx, but got {save_as} instead.")


def save_as_json(conll: Path, language: str, normalized: bool, annotation: str) -> None:
    """Save as json format"""
    text, labels = read_conll_file(conll)[0]
    json_object = json.dumps(
        {
            "Timestamp": str(datetime.now()), "Language": language,
            "Normalization": normalized, "Annotation": annotation,
            "Metadata": labels, "text": text
        },
        indent=4
    )

    with open(change_suffix(conll, "json"), "w", encoding="utf-8") as output_file:
        output_file.write(json_object)


def save_as_xlsx(conll: Path, language: str, normalized: bool, annotation: str) -> None:
    """Save as xlsx format"""
    XlsxAnnotationWriter(change_suffix(conll, "xlsx")).load(conll, language, normalized, annotation)


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
