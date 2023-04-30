"""Type declaration used for statistics

"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Tuple, TypeVar, Optional

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text


D = List[defaultdict]
B = TypeVar("B", Token, Sentence, Paragraph, Text)  # Block
C = TypeVar("C", Sentence, Paragraph, Text)  # Context
S = TypeVar(  # Serialization
    "S",
    bound=Tuple[
        # scalars: chars, token_count, words, syllables, polysyllables, misspells, compounds
        int, int, int, int, int, int, int,
        # scalars: 3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc
        int, int, int, int, int, int, int, int, int,
        # scalars: advance_cefr, advance_noun_or_verb
        int, int, 
        # sents
        int,
        # freq_<form|norm|lemma>_dict_<upos|xpos>, xpos_dict, word_dict
        D, D, D, D, D, D, D, D,
        # counter for token length, sentence length, cefr, wpm;  a list of types
        Counter, Counter, Counter, Counter, List[str]
    ]
)
V = TypeVar("V", int, float)


@dataclass
class Feature:
    scalar: Optional[V] = None
    mean: Optional[V] = None
    median: Optional[V] = None
