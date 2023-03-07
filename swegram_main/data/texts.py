"""Text Module

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List, Any

from swegram_main.data.paragraphs import Paragraph
from swegram_main.lib.utils import get_size

@dataclass
class State:

    tokenized: bool = True
    normalized: bool = False
    tagged: bool = False
    parsed: bool = False


@dataclass
class Text:

    # data
    paragraphs: List[Paragraph]

    # properties
    text_id: str
    language: str
    filename: Path
    labels: Optional[Dict[str, str]] = None
    activated: bool = False

    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None

    morphological: Optional[Any]            = None
    morphological_average: Optional[Any]    = None

    lexical: Optional[Any]                  = None
    lexical_average: Optional[Any]          = None

    syntactic: Optional[Any]                = None
    syntactic_average: Optional[Any]        = None

    @property
    def states(self) -> State:
        ...

    @property
    def filesize(self):
        return get_size(self.filename)

    @property
    def has_label(self):
        return len(self.labels) != 0

    def __str__(self):
        return "\n  ".join([str(p) for p in self.paragraphs])
