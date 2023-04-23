"""module of preprocessing text handling before applying any linguistic annotations
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from swegram_main.data.texts import TextDirectory as TD
from swegram_main.pipeline.checker import checker
from swegram_main.lib.utils import cut, FileContent, MetaFormatError


class RestoreFileError(Exception):
    """Restore file error"""


def preprocess(input_path: Path, output_dir: Path, model) -> List[TD]:
    text_index = 0
    text_instances: List[TD] = []
    try:
        file_content = FileContent(input_path).get()
        meta = None
        component = next(file_content)
        while True:
            text_path = Path(os.path.join(output_dir, f"{input_path.stem}_{text_index}.txt"))
            if isinstance(component, dict):
                meta = component
                component = next(file_content)
            text = TD(filepath=text_path, meta=meta)
            with open(text.filepath, "w", encoding="utf-8") as input_file:
                while True:
                    if isinstance(component, str):
                        input_file.write(component)
                    elif isinstance(component, dict):
                        break
                    else:
                        raise MetaFormatError(f"Invalid format, got {type(component)}: {component}")
                    component = next(file_content)
            text_instances.append(text)
            text_index += 1
            meta = component
            component = next(file_content)
    except StopIteration:
        text_instances.append(text)

    restore_text = lambda text: text if input_path.suffix != ".conll" else restore(text, output_dir, model)
    return [restore_text(text) for text in text_instances if os.path.getsize(text.filepath)]


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
        raise RestoreFileError(f"Unknow model to restore tagged line: {model}")


def _restore(
    from_: str, filepath: Path, workspace: Path, model: str = "efselab",
    normalized: Optional[bool] = None
) -> None:
    """Restore the uploaded annotated text into a format that allows pipeline process further
    """
    restore_tokenized_line_helper = lambda line: restore_tokenized_line(line, model)
    restore_normalized_line_helper = lambda line: restore_normalized_line(line, model)
    if from_ == "tokenized":
        cut(
            restore_tokenized_line_helper, filepath,
            output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok")
        )

    elif from_ == "normalized":
        cut(
            restore_tokenized_line_helper, filepath,
            output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok")
        )
        cut(
            restore_normalized_line_helper, filepath,
            output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}spell")
        )

    elif from_ == "tagged":
        if normalized:
            cut(
                restore_tokenized_line_helper, filepath,
                output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tok")
            )
            cut(
                restore_normalized_line_helper, filepath,
                output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}spell")
            )
        cut(
            lambda line: restore_tagged_line(line, model, normalized),
            filepath,
            output_path=workspace.joinpath(f"{filepath.stem}{os.path.extsep}tag")
        )
    else:
        raise RestoreFileError(f"Unknown state for annotation: {from_}")


def restore(text: TD, output_dir: Path, model: str) -> TD:
    """restore annotated text
    """
    input_path = text.filepath
    temp_dir = tempfile.TemporaryDirectory()
    workspace = Path(temp_dir.name)
    normalized, tagged, parsed = checker(input_path, model)
    if parsed:
        from_ = "parsed"
    elif tagged:
        from_ = "tagged"
    elif normalized:
        from_ = "normalized"
    else:
        from_= "tokenized"
    _restore(from_, input_path, workspace, model, normalized)
    shutil.copytree(workspace, output_dir, dirs_exist_ok=True)
    return text
