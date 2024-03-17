import re
import subprocess
import tempfile
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Union

from swegram_main.data.features import Feature
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.sentences import Sentence
from swegram_main.data.texts import Text
from swegram_main.data.tokens import Token
from swegram_main.handler.handler import load_dir
from swegram_main.lib.logger import get_logger
from swegram_main.pipeline.pipeline import Pipeline


SPLIT_HEADER = "------WebKitFormBoundary"


def convert_attribute_name(name: str) -> str:
    return {
        "text_id": "uuid",
        "filesize": "_filesize",
        "token_index": "index"
    }.get(name, name)


def convert_attribute_value(value: Any) -> Union[int, bool, str, Any]:
    if isinstance(value, (int, bool, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, OrderedDict):
        for k, v in value.items():
            if isinstance(v, Feature):
                value[k] = v.json
    return value


def get_size_and_format(size_bytes: int) -> str:
    # Define the units and their respective sizes
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = size_bytes
    unit = 0

    # Iterate through units and convert size until it's less than 1024
    while size >= 1024 and unit < len(units) - 1:
        size /= 1024.0
        unit += 1

    # Format the size with two decimal places
    formatted_size = "{:.2f} {}".format(size, units[unit])
    return formatted_size


def _get_pattern(key: str) -> str:
    return fr'(?<={key}=").+(?=")'


def parse_item(item: List[str]) -> Dict[str, Any]:

    head, *body = item
    if "file_to_annotate" in head:
        return {
            "filename": re.search(_get_pattern("filename"), head).group(),
            "content_type": body[0].lstrip("Content-Type:").strip(),
            "raw_text": "\n".join(body[2:])
        }
    elif "pasted_text" in head:
        return {"raw_text": "\n".join(body[1:])}
    else:
        name = re.search(_get_pattern("name"), head).group()
        value = body[-1].strip()
        if value == "true":
            value = True
        elif value == "false":
            value = False
        return {name: value}


def parse_payload(payload: bytes) -> Dict[str, Any]:
    data_lines = payload.decode().splitlines()
    data, item = {}, []
    while data_lines:
        line = data_lines.pop(0)
        if line.startswith(SPLIT_HEADER):
            if item and item[0].strip():
                data.update(parse_item(item))
                item = []
        else:
            item.append(line)
    if item and item[0].strip():
        data.update(parse_item(item))
    return data


def _serialize_item(item: Union[Text, Paragraph, Sentence, Token]) -> Dict[str, Any]:

    serialized_item = {
        convert_attribute_name(attr): convert_attribute_value(getattr(item, attr))
        for attr in dir(item) if not attr.startswith("__") if attr not in ["paragraphs", "sentences", "tokens"]
    }

    if isinstance(item, Text):
        serialized_item.update({"paragraphs": [_serialize_item(p) for p in item.paragraphs]})
    elif isinstance(item, Paragraph):
        serialized_item.update({"sentences": [_serialize_item(s) for s in item.sentences]})
    elif isinstance(item, Sentence):
        serialized_item.update({"tokens": [_serialize_item(t) for t in item.tokens]})

    return serialized_item


def generate_filename(filename: str, index: int) -> str:
    """Generate filename"""
    file, extention = filename.rsplit(".", maxsplit=1)
    return f"{file}_{index}.{extention}"


def save_text(raw_text: str, target_path: Path) -> None:
    with open(target_path, mode="w", encoding="utf-8") as f:
        f.write(raw_text)


def run_swegram(language: str, **kwargs) -> List[Dict[str, Any]]:
    """Annotate text and return a dict to be stored into database"""
    states = {
        "tokenized": kwargs.get("checkTokenize", True),
        "normalized": kwargs.get("checkNormalization", False),
        "tagged": kwargs.get("checkPOS", False),
        "parsed": kwargs.get("checkPOS", False)
    }

    normalize = kwargs.get("checkNormalization")
    parse = kwargs.get("checkPOS")
    tokenize = kwargs.get("checkTokenize")

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt") as input_file:
        with tempfile.TemporaryDirectory() as output_dir:
            save_text(kwargs["raw_text"], input_file.name)
            input_file.flush()

            pipeline = Pipeline(
                input_path=Path(input_file.name), output_dir=Path(output_dir), language=language
            )

            if normalize:
                pipeline.normalize()

            # parse <- tag <- tokenize
            # tag is not an optional in frontend
            if parse:
                pipeline.parse()
            elif tokenize and not normalize:
                pipeline.tokenize()
            else:
                raise Exception(f"Invalid annotation request, {kwargs}")
            pipeline.postprocess()

            texts: List[Text] = load_dir(
                input_dir=Path(output_dir), language=language, include_tags=[], exclude_tags=[], parsed=parse
            )
            filename = kwargs.get("filename", f"Pasted at {str(datetime.now())}")
            return [{
                **_serialize_item(text), **states, "filename": generate_filename(filename, index)}
                for index, text in enumerate(texts, 1)
            ]
