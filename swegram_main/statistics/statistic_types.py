"""Type declaration used for statistics

"""
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple, TypeVar

from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text, Corpus


A = TypeVar("A", str, int) # Argument for e.g. lemma incsc computation
B = TypeVar("B", Token, Sentence, Paragraph, Text, Corpus)  # Block
C = TypeVar("C", Sentence, Paragraph, Text)  # Context
D = List[defaultdict]
F = TypeVar("F", bound=Tuple[str, callable, Optional[callable], Dict[str, List[Tuple[str, Any]]], Dict[str, Any]]) # Feature parameter
S = TypeVar(  # Serialization
    "S",
    bound=Tuple[
        # scalars: chars, token_count, words, syllables, polysyllables, misspells, compounds
        int, int, int, int, int, int, int,
        # scalars: 3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc
        int, int, int, int, int, int, int, int, int,
        # scalars: advance_cefr, advance_noun_or_verb
        int, int,
        # scalars: long_arcs, left_arcs, right_arcs, pre_modifier, post_modifier,
        int, int, int, int, int,
        # scalars: subordinate_nodes, relative_clause_nodes, preposition_nodes
        int, int, int,
        # sents
        int,
        # freq_<form|norm|lemma>_dict_<upos|xpos>, xpos_dict, word_dict
        D, D, D, D, D, D, D, D,
        # counter for token length, sentence length, cefr, wpm;
        Counter, Counter, Counter, Counter,
        # list of types, list of token depths
        List[str], List[Tuple[int]]
    ]
)
