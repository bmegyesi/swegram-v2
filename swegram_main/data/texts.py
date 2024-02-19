"""Text Module

"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, List, Any

from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.metadata import convert_labels_to_list
from swegram_main.lib.utils import get_size, change_suffix

@dataclass
class State:

    tokenized: bool = True
    normalized: bool = False
    tagged: bool = False
    parsed: bool = False


@dataclass
class Text:  # pylint: disable=too-many-instance-attributes

    # data
    paragraphs: List[Paragraph]

    # properties
    text_id: str
    language: str
    filename: Path  # The filename can be shared across different texts 

    elements: Optional[str] = "paragraphs"
    labels: Optional[Dict[str, str]] = None
    activated: bool = False

    # state
    tokenized: bool = True
    normalized: bool = False
    tagged: bool = False
    parsed: bool = False

    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None
    morph: Optional[Any]                    = None
    lexical: Optional[Any]                  = None
    syntactic: Optional[Any]                = None


    @property
    def filesize(self):
        return get_size(self.filename)

    @property
    def has_label(self):
        return bool(self.labels)

    @property
    def metadata(self):
        return convert_labels_to_list(self.labels) if self.labels else []

    def __str__(self):
        return "\n  ".join([str(p) for p in self.paragraphs])


@dataclass
class Corpus:

    # data
    texts: List[Text]

    # properties
    language: str
    elements: Optional[str] = "texts"

    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None
    morph: Optional[Any]                    = None
    lexical: Optional[Any]                  = None
    syntactic: Optional[Any]                = None

@dataclass
class TextDirectory:
    filepath: Path
    meta: Dict[str, str] = field(default_factory=dict)

    def generate_path(self, suffix) -> Path:
        return change_suffix(self.filepath, suffix)

    @property
    def tok(self):
        return self.generate_path("tok")

    @property
    def spell(self):
        return self.generate_path("spell")

    @property
    def tag(self):
        return self.generate_path("tag")

    @property
    def conll(self):
        return self.generate_path("conll")
