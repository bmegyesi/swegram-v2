import inspect
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from swegram_main.data.sentences import Sentence


@dataclass
class Paragraph:

    text_uuid: str
    language: str
    sentences: List[Sentence]
    elements: Optional[str] = "sentences"
    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None
    morph: Optional[Any]                    = None
    lexical: Optional[Any]                  = None
    syntactic: Optional[Any]                = None

    def to_dict(self) -> Dict[str, Any]:
        # attributes defined from dataclass 
        data = {k: v for k, v in asdict(self).items() if not k.startswith("__") and k != "sentences"}
        # properties
        props = {
            name: getattr(self, name)
            for name, value in inspect.getmembers(type(self))
            if isinstance(value, property)
        }
        # dynamically added data
        extra = {
            k: v for k, v in vars(self).items() if k != "sentences" and k not in data
        }
        return {**data, **props, **extra, "sentences": [s.to_dict() for s in self.sentences]}

    def __str__(self) -> str:
        return " ".join([str(s) for s in self.sentences])
