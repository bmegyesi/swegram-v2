"""Module of sentence data structure
"""
from dataclasses import dataclass
from typing import Any, List, Optional

from swegram_main.data.tokens import Token
from swegram_main.lib.utils import is_a_ud_tree


@dataclass
class Sentence:
    """Data structure for sentence instance"""
    text_id: str
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

    def __str__(self):
        sentence = str(self.tokens[0])
        for token in self.tokens[1:]:
            if token.upos != "PUNCT":
                sentence += f" {str(token)}"
            else:
                sentence += str(token)
        return sentence
