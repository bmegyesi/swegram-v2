from collections import Counter, defaultdict
from typing import List, Tuple, TypeVar

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text


D = List[defaultdict]
B = TypeVar("B", Token, Sentence, Paragraph, Text)  # Block
C = TypeVar("C", Token, Sentence, Paragraph, Text)  # Context
S = TypeVar(
    "S",
    bound=Tuple[
        # scalars: chars, token_count, words, syllables, polysyllables, misspells, compounds, sents
        int, int, int, int, int, int, int, int,
        # freq_<form|norm|lemma>_dict_<upos|xpos>
        D, D, D, D, D, D,
        # counter for token|sentence length; a list of types
        Counter, Counter, List[str]
    ]
)
