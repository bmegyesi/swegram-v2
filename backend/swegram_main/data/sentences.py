"""Module of sentence data structure
"""
import inspect
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from swegram_main.data.tokens import Token
from swegram_main.lib.utils import is_a_ud_tree


@dataclass
class Sentence:
    """Data structure for sentence instance"""
    text_uuid: str
    language: str
    tokens: List[Token]
    elements: Optional[str] = "tokens"

    # statistics
    general: Optional[Any]       = None
    readability: Optional[Any]   = None
    morph: Optional[Any]         = None
    lexical: Optional[Any]       = None
    syntactic: Optional[Any]     = None

    types: Optional[List[str]]   = None
    
    @property
    def ud_tree(self) -> bool:
        try:
            return is_a_ud_tree([int(token.head) for token in self.tokens])
        except ValueError:  # raised error when token.head is _
            return False

    def to_dict(self) -> Dict[str, Any]:
        # attributes defined from dataclass 
        data = {k: v for k, v in asdict(self).items() if not k.startswith("__")}
        # properties
        props = {
            name: getattr(self, name)
            for name, value in inspect.getmembers(type(self))
            if isinstance(value, property)
        }
        # dynamically added data
        extra = {
            k: v for k, v in vars(self).items() if k not in data
        }
        return {**data, **props, **extra}

    def __str__(self):
        sentence = str(self.tokens[0])
        for token in self.tokens[1:]:
            if token.upos != "PUNCT":
                sentence += f" {str(token)}"
            else:
                sentence += str(token)
        return sentence
