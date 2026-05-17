"""Text Module

"""
import inspect
from dataclasses import dataclass, field, asdict
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
    text_uuid: str
    language: str
    filename: Path  # The filename can be shared across different texts
    # uuid: str

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

    @filesize.setter
    def filesize(self, value):
        return value

    @property
    def has_label(self):
        return bool(self.labels)

    @has_label.setter
    def has_label(self, value):
        return value

    @property
    def metadata(self):
        return convert_labels_to_list(self.labels) if self.labels else []

    @metadata.setter
    def metadata(self, value):
        return value

    def to_dict(self) -> Dict[str, Any]:
        # attributes defined from dataclass 
        data = {k: v for k, v in asdict(self).items() if not k.startswith("__") and k != "paragraphs"}
        # properties
        props = {
            name: getattr(self, name)
            for name, value in inspect.getmembers(type(self))
            if isinstance(value, property)
        }
        # dynamically added data
        extra = {
            k: v for k, v in vars(self).items() if k != "paragraphs" and k not in data
        }
        return {**data, **props, **extra}

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
    def spell(self) -> Path:
        return self.generate_path("spell")

    @property
    def tok(self) -> Path:
        return self.generate_path("tok")

    @property
    def spell(self) -> Path:
        return self.generate_path("spell")

    @property
    def tag(self) -> Path:
        return self.generate_path("tag")

    @property
    def conll(self) -> Path:
        return self.generate_path("conll")
