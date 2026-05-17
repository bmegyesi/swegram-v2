"""Converter module

Supported and tested formats:
1. docx
2. RTF
3. ODT
4. RST

More on pandoc
https://pandoc.org/MANUAL.html
"""
import os
import json
import subprocess
from itertools import chain
from typing import Any
from pathlib import Path


PANDOC = os.environ.get("PANDOC_PATH")  # SET PANDOC PATH  e.g. PANDOC = "./lib/pandoc-2.19.2/bin/pandoc"
CONLLU_FOMRAT = "conll"
VALID_FORMATS = ["docx", "rft", "odt", "rst"]
FORMAT_TYPES = ["Strong", "Emph", "MetaInlines"]


class ConvertError(Exception):
    """Convert error"""


class InvalidFormat(Exception):
    """Invalid format"""


class Converter:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath 

    def parse(self):
        converted = self._convert()
        if isinstance(converted, dict):
            meta = self.parse_meta(converted)
            yield from chain(meta, self.parse_blocks(converted))
        else:
            with open(self.filepath, mode="r", encoding="utf-8") as input_file:
                line = input_file.readline()
                while line:
                    yield line
                    line = input_file.readline()

    def _convert(self):
        try:  # pylint: disable=too-many-try-statements
            suffix = self.filepath.suffix.lstrip(".")
            if suffix in ["txt", CONLLU_FOMRAT]:
                return None
            if suffix not in VALID_FORMATS:
                raise InvalidFormat
            response = subprocess.run(
                f"{PANDOC} -f {suffix} -t json {self.filepath}".split(), capture_output=True, check=False
            )
            if response.stderr:
                raise ConvertError(response.stderr.decode())
            return json.loads(response.stdout.decode())
        except InvalidFormat as err:
            raise ConvertError(f"The format {suffix} is not supported.") from err
        except Exception as err:
            raise ConvertError(f"Failed to covert: {err}") from err

    def parse_meta(self, json_obj: Any):
        if "meta" in json_obj:
            if "title" in json_obj["meta"]:
                yield self.parse_tag(json_obj["meta"]["title"])
        yield

    def parse_blocks(self, json_obj: Any):
        if "blocks" in json_obj:
            for block in json_obj["blocks"]:
                yield self.parse_tag(block)
        else:
            yield

    def parse_tag(self, chunk: Any) -> str:
        tag = chunk["t"]
        if tag == "Space":
            return " "
        if tag == "Str":
            return chunk["c"]
        if tag == "Para":
            return "".join([self.parse_tag(c) for c in chunk["c"]]) + "\n"
        if tag in FORMAT_TYPES:
            return "".join([self.parse_tag(c) for c in chunk["c"]])
        if tag == "Header":
            return "".join([self.parse_tag(c) for c in chunk["c"][2]])
        return ""
