"""module of preprocessing text handling before applying any linguistic annotations
"""
from pathlib import Path
from typing import Dict, Iterator, Union

from swegram_main.pipeline.converter import Converter
from swegram_main.data.metadata import parse_metadata

class FileContent:

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def _convert(self):
        yield from Converter(self.filepath).parse()

    def get(self) -> Iterator[Union[Dict[str, str], str]]:
        for line in self._convert():
            if not line:
                continue
            metadata = parse_metadata(line)
            if metadata is None:
                yield line
            else:
                yield metadata
