"""Module of sentence data structure
"""
from dataclasses import dataclass
from collections import Counter
from typing import Any, List, Optional, Tuple

from swegram_main.data.tokens import Token
from swegram_main.lib.tree import is_ud_tree


@dataclass
class Sentence:
    """Data structure for sentence instance"""
    text_id: str
    tokens: List[Token]

    # statistics
    general: Optional[Any] = None
    readability: Optional[Any] = None
    morphological: Optional[Any] = None
    lexical: Optional[Any] = None
    syntactic: Optional[Any] = None

    @property
    def ud_tree(self) -> bool:
        try:
            return is_ud_tree([int(token.head) for token in self.tokens]) is True
        except ValueError:  # raised error when token.head is _
            return False

    @property
    def types(self) -> List[Tuple[str, int]]:
        return Counter([str(token) for token in self.tokens]).most_common()

    def __str__(self):
        sentence = str(self.tokens[0])
        for token in self.tokens[1:]:
            if token.upos != "PUNCT":
                sentence += f" {str(token)}"
            else:
                sentence += str(token)
        return sentence
