import re
import tempfile
import pytz
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict
from server.pipeline import annotate_file


SPLIT_HEADER = "------WebKitFormBoundary"


def _get_pattern(key: str) -> str:
    return fr'(?<={key}=").+(?=")'


def parse_item(item: List[str]) -> Dict[str, Any]:
    head, *body = item
    if "filename" in head:
        return {
            "filename": re.search(_get_pattern("filename"), head).group(),
            "content_type": body[0].lstrip("Content-Type:").strip(),
            "raw_text": "\n".join(body[2:])
        }
    if "pasted_text" in head:
        timestamp = datetime.now(tz=pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")
        return {"raw_text": "\n".join(body[1:]), "filename": f"Pasted at {timestamp}.txt"}
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


def run_swegram(language: str, **kwargs):
    """Annotate file"""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt") as input_file:
        with tempfile.TemporaryDirectory() as output_dir:
            annotate_file(language=language, filepath=input_file.name, output_dir=output_dir, **kwargs)
