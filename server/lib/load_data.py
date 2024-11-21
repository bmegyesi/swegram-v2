import re
import tempfile
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Union

import pytz

from sqlalchemy.orm import Session

from server.lib.exceptions import ServerError
from server.lib.tasks import create_task, update_task, read_task, create_taskgroup, update_taskgroup, read_taskgroup
from server.lib.utils import convert_attribute_name, convert_attribute_value
from server.models import TaskGroup, TaskGroupProcessBar

from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.sentences import Sentence
from swegram_main.data.texts import Text
from swegram_main.data.tokens import Token
from swegram_main.handler.handler import load_dir
from swegram_main.pipeline.pipeline import Pipeline


SPLIT_HEADER = "------WebKitFormBoundary"


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
    if "pasted_text" in head:
        return {"raw_text": "\n".join(body[1:])}
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


def ts() -> str:
    """get timestamp for now"""
    return datetime.now(tz=pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")


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
            # Update taskgroup here
            # Create task from here

            if normalize:
                pipeline.normalize()
                # Update tasks and taskgroup

            # parse <- tag <- tokenize
            # tag is not an optional in frontend
            if parse:
                pipeline.parse()
                # Update tasks and taskgroup
            elif tokenize and not normalize:
                pipeline.tokenize()
                # Update tasks and taskgroup
            else:
                raise ServerError(f"Invalid annotation request, {kwargs}")
            pipeline.postprocess()

            # Convert conll file into structured data
            texts: List[Text] = load_dir(
                input_dir=Path(output_dir), language=language, include_tags=[], exclude_tags=[], parsed=parse
            )
            filename = kwargs.get("filename", f"Pasted at {ts()}.txt")
            return [{
                **_serialize_item(text), **states, "filename": generate_filename(filename, index)}
                for index, text in enumerate(texts, 1)
            ]


def commit(database: Session, instance: object, add: bool = False, refresh: bool = True) -> None:
    try:
        if add:
            database.add(instance)
        database.commit()
        if refresh:
            database.refresh(instance)
    except Exception as err:
        database.rollback()
        raise ServerError(f"Failed to commit to database") from err


def create_text_helper(language: str, data: bytes, database: Session) -> None:

    try:
        taskgroup_created_response = create_taskgroup()
        taskgroup_id = taskgroup_created_response["taskgroup_id"]
        taskgroup_processbar = TaskGroupProcessBar(taskgroup_id=taskgroup_id)
        commit(taskgroup_processbar, add=True)

        data = parse_payload(data)
        taskgroup_processbar.raw_texts_checked = True
        taskgroup_processbar.raw_texts_checked_ts = ts()
        commit(taskgroup_processbar)

        texts = run_swegram(language, **data)
        for text_data in texts:
            paragraphs = text_data["paragraphs"]
            del text_data["paragraphs"]
            text = Text(**text_data)
            try:
                database.add(text)
                database.commit()
                database.refresh(text)
                text.load_data(paragraphs, database)
            except Exception as err:
                database.rollback()
                raise ServerError("Failed to create Text instance in the database.") from err
    finally:
        ...
