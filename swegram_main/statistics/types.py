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
        # scalars: chars, token_count, words, syllables, polysyllables, misspells, compounds
        int, int, int, int, int, int, int,
        # sclars: 3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc
        int, int, int, int, int, int, int, int, int,
        # sents
        int,
        # freq_<form|norm|lemma>_dict_<upos|xpos>, xpos_dict, word_dict
        D, D, D, D, D, D, D, D,
        # counter for token|sentence length; a list of types
        Counter, Counter, List[str]
    ]
)
