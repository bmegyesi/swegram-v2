"""General features:

token
word
word length
spelling error
sentences
sentence length (n words) (excluding punctuations)
paragraphs
paragraph length (n words) (excluding punctuations)
paragraph length (n sentences)
"""
import math
import re
from collections import Counter, OrderedDict, defaultdict
from copy import copy
from typing import List, Tuple

from swegram_main.config import (
    KELLY_EN, KELLY_SV, ADVANCE_CEFR_LEVELS, WPM_SV,
    MODIFIER_DEPREL_LABELS, SUBORDINATION_DEPREL_LABELS,
    LONG_ARC_THRESHOLD
)
from swegram_main.data.features import Feature
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.sentences import Sentence
from swegram_main.data.texts import Text
from swegram_main.data.tokens import Token
from swegram_main.lib.utils import (
    get_path, get_child_nodes, is_a_ud_tree,
    merge_digits_for_fields,
    mean, median, r2, merge_dicts_for_fields
)
from swegram_main.statistics.types import B, S


class SerializationError(Exception):
    """Serialization Error"""


ENGLISH_VOWELS = "aoueiy"
SWEDISH_VOWELS = f"{ENGLISH_VOWELS}åöä"


def _syllable_count_en(word: str) -> int:
    word = word.lower()
    count = 1 if word[0] in ENGLISH_VOWELS else 0
    for index, c in enumerate(word[1:-1], 2):
        if c in ENGLISH_VOWELS and word[index] not in ENGLISH_VOWELS:
            count += 1
    if word.endswith("e"):
        count -= 1
    return max(count, 1)


def _syllable_count_sv(word: str) -> int:
    word = word.lower()
    found_vowels = [c for c in word if c in SWEDISH_VOWELS]
    if found_vowels:
        # journalist is the exceptional word where ou is counted as one syllable
        if not re.search("journalist", word):
            return len(found_vowels)
        return len(found_vowels) - 1
    return 1


def _serialize_tokens(tokens: List[Token], lang: str) -> S:

    _syllable_count = _syllable_count_en if lang == "en" else _syllable_count_sv
    polysyllables, syllables, misspells, compounds, words = 0, 0, 0, 0, len(tokens)
    # The following scalars are used for morphological feature calculation
    _3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc = [0 for _ in range(9)]
    # The following scalars are used for lexical feature calculation
    advance_cefr, advance_noun_or_verb = 0, 0
    types = set()

    freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos = [defaultdict(int) for _ in range(3)]
    freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos = [defaultdict(int) for _ in range(3)]
    upos_dict, xpos_dict, word_dict = [defaultdict(int) for _ in range(3)]  # used for readability features

    token_length_list = [] # the length of each token

    # Lexical features related
    cefr_list = []
    wpm_sv_list = []
    kelly_dict = KELLY_EN if lang == "en" else KELLY_SV

    # Syntactical features related
    depth_list: List[Tuple[int, ...]] = []
    long_arcs, left_arcs, right_arcs, pre_modifier, post_modifier = 0, 0, 0, 0, 0
    subordinate_nodes, relative_clause_nodes, preposition_nodes = [set() for _ in range(3)]

    try:
        response = is_a_ud_tree([token.head for token in tokens])
        if response is not True:
            raise ValueError(response)
    except ValueError:
        heads = None
    else:
        heads = [None, *[int(token.head) for token in tokens]]

    for index, token in enumerate(tokens, 1):
        form, norm, lemma = token.form.lower(), token.norm.lower(), token.lemma.lower()
        upos, xpos, feats = token.upos, token.xpos, token.feats
        freq_form_dict_upos[f"{form}_{upos}"] += 1
        freq_norm_dict_upos[f"{norm}_{upos}"] += 1
        freq_lemma_dict_upos[f"{lemma}_{upos}"] += 1
        freq_form_dict_xpos[f"{form}_{xpos}"] += 1
        freq_norm_dict_xpos[f"{norm}_{xpos}"] += 1
        freq_lemma_dict_xpos[f"{lemma}_{xpos}"] += 1
        upos_dict[upos] += 1
        xpos_dict[xpos] += 1

        word = norm if norm != "_" else form
        word_dict[word] += 1

        syllable_length = _syllable_count(word)
        syllables += syllable_length

        if syllable_length > 2:
            polysyllables += 1
        token_length_list.append(len(word))

        if norm not in [form, "_"]:
            misspells += 1

        if "-" in token.token_index:
            compounds += 1

        types.add(norm) if norm != "_" else types.add(form)

        if upos == "PUNCT":
            words -= 1

        #<start----------used for morph features-----------start>
        if "Gender=Neut" in feats and upos == "NOUN":
            neut_noun += 1
        elif "Number=Sing" in feats and upos == "PRON":
            _3sg_pron += 1
        elif word.endswith("s") and upos == "VERB":
            s_verb += 1

        if "VerbForm=Part" in feats:
            if "Tense=Pres" in feats:
                pres_pc += 1
            elif "Tense=Past" in feats:
                past_pc += 1
        elif "VerbForm=Fin" in feats:
            if "Tense=Pres" in feats:
                pres_verb += 1
            elif "Tense=Past" in feats:
                past_verb += 1
        elif "VerbForm=Sup" in feats:
            sup_verb += 1 

        if "PronType=Int" in feats or "PronType=Rel" in feats:
            rel_pron += 1
        #<end------------used for morph features-------------end>

        #<start----------used for lexical features----------start>
        entry = f"{lemma}|{upos}"
        cefr = kelly_dict.get(entry)
        if cefr:
            cefr_list.append(cefr)
            if cefr in ADVANCE_CEFR_LEVELS:
                advance_cefr += 1
                if upos in ["NOUN", "VERB"]:
                    advance_noun_or_verb += 1
        if lang == "sv":
            wpm = WPM_SV.get(entry)
            if wpm:
                wpm_sv_list.append(r2(math.log(wpm)))
        #<end------------used for lexical features------------end>

        #<start----------used for syntactic features--------start>
        if heads:
            token_depth = tuple(get_path(index, heads))
            depth_list.append(token_depth)
            if len(token_depth) > LONG_ARC_THRESHOLD:
                long_arcs += 1
            if heads[index] < index:
                left_arcs += 1
            elif heads[index] > index:
                right_arcs += 1
            else:
                raise Exception("Error during syntax annotation parsing")
            if token.deprel.startswith(tuple(MODIFIER_DEPREL_LABELS)):
                if heads[index] < index:
                    post_modifier += 1
                elif heads[index] > index:
                    pre_modifier += 1
                else:
                    raise Exception("Error during syntax annotation parsing")
            elif token.deprel == "case":
                preposition_nodes.add(index)
                preposition_nodes = preposition_nodes.union(get_child_nodes(index, copy(heads)))
            else:
                if token.deprel.startswith(tuple(SUBORDINATION_DEPREL_LABELS)):
                    subordinate_nodes = subordinate_nodes.union(get_child_nodes(index, copy(heads)))
                if "rel" in token.deprel:
                    relative_clause_nodes.add(index)
                    relative_clause_nodes = relative_clause_nodes.union(get_child_nodes(index, copy(heads)))
        #<end------------used for syntactic features----------end>


    return  sum(token_length_list), len(tokens), words, syllables, polysyllables, misspells, compounds, \
            _3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc, \
            advance_cefr, advance_noun_or_verb, \
            long_arcs, left_arcs, right_arcs, pre_modifier, post_modifier, \
            len(subordinate_nodes), len(relative_clause_nodes), len(preposition_nodes), \
            1, \
            freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
            freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos, \
            upos_dict, xpos_dict, word_dict, \
            Counter(token_length_list), Counter([len(tokens)]), Counter(cefr_list), Counter(wpm_sv_list), \
            list(types), depth_list


def _merge_counters(blocks: List[B], fields: List[str]) -> List[Counter]:
    counters = []
    for field in fields:
        counter = Counter()
        for block in blocks:
            for key, value in getattr(block.general, field).items():
                counter[key] += value
        counters.append(counter)
    return counters


def _union(blocks: List[B], field: str) -> List[str]:
    union = set()
    for block in blocks:
        union = union.union(getattr(block.general, field))
    return list(union)


def _serialize(blocks: List[B], lang: str) -> S:
    if isinstance(blocks[0], Token):
        return _serialize_tokens(blocks, lang)
    elif isinstance(blocks[0], Sentence):
        sents = len(blocks)
    elif isinstance(blocks[0], (Paragraph, Text)):
        sents = sum([block.general.sents for block in blocks])
    else:
        raise SerializationError(f"Unknown block type: {type(blocks[0])}")
    scalars = merge_digits_for_fields(blocks, CountFeatures.SCALAR_FIELDS[:-1])  # sents is computed separately
    freqs = merge_dicts_for_fields(blocks, CountFeatures.FREQ_FIELDS)
    counters = _merge_counters(blocks, CountFeatures.COUNTER_FIELDS)
    types = _union(blocks, CountFeatures.UNION_FIELD)
    depth_list = [t for block in blocks for t in getattr(block.general, CountFeatures.LIST_FIELD)]

    return *scalars, sents, *freqs, *counters, types, depth_list


class CountFeatures:

    # Field Declaration
    SCALAR_FIELDS = [
        "chars", "token_count", "words", "syllables", "polysyllables", "misspells", "compounds",
        "_3sg_pron", "neut_noun", "s_verb", "rel_pron", "pres_verb", "past_verb", "sup_verb", "pres_pc", "past_pc",
        "advance_cefr", "advance_noun_or_verb",
        "long_arcs", "left_arcs", "right_arcs", "pre_modifier", "post_modifier",
        "subordinate_nodes", "relative_clause_nodes", "preposition_nodes",
        "sents",
    ]
    FREQ_FIELDS = [
        "freq_form_dict_upos", "freq_norm_dict_upos", "freq_lemma_dict_upos",
        "freq_form_dict_xpos", "freq_norm_dict_xpos", "freq_lemma_dict_xpos",
        "upos_dict", "xpos_dict", "word_dict"
    ]
    COUNTER_FIELDS = ["token_length_counter", "sentence_length_counter", "cefr_counter", "wpm_sv_counter"]
    UNION_FIELD = "types"
    LIST_FIELD = "depth_list"
    FIELDS = [*SCALAR_FIELDS, *FREQ_FIELDS, *COUNTER_FIELDS, UNION_FIELD, LIST_FIELD]

    # Feature Declaration
    SENTENCE_FEATURES = ["Token-count", "Type-count", "Spelling erros", "Compound errors", "Word length"]

    _Sentences, _Sentence_length = "Sentences", "Sentence length (n words)"
    PARAGRAPH_FEATURES = [_Sentences, _Sentence_length]

    _Paragraphs, _Paragraph_length_word = "Paragraphs", "Paragraph length (n words)"
    _Paragraph_length_sentence = "Paragraph length (n sentences)"
    TEXT_FEATURES = [_Paragraphs, _Paragraph_length_word, _Paragraph_length_sentence]

    def __init__(self, content: List[B], lang: str) -> None:
        self.blocks = content
        self.lang = lang
        self._set_fields()
        self._set_feats()

    def _set_fields(self) -> None:
        for key, value in zip(self.FIELDS, _serialize(self.blocks, self.lang)):
            setattr(self, key, value)
        self.type_count = len(self.types)

    def _set_feats(self) -> None:
        self.data = OrderedDict()
        self._set_sentence_features()
        if not isinstance(self.blocks[0], Token):
            self._set_paragraph_features()
        if not isinstance(self.blocks[0], (Token, Sentence)):
            self._set_text_features()

    def _set_sentence_features(self) -> None:
        for feature_name, attribute in zip(
            self.SENTENCE_FEATURES,
            ["token_count", "type_count", "misspells", "compounds"]
        ):
            if not isinstance(self.blocks[0], Token):
                scalar_list = [getattr(block.general, attribute) for block in self.blocks]
                self.data[feature_name] = Feature(
                    scalar=getattr(self, attribute), mean=mean(scalar_list), median=median(scalar_list)
                )
            else:
                self.data[feature_name] = Feature(scalar=getattr(self, attribute))
        self.data["Word length"] = Feature(
            mean=r2(self.chars, self.token_count), median=median(self.token_length_counter)
        )

    def _set_paragraph_features(self) -> None:
        self.data[self._Sentences] = Feature(scalar=self.sents)
        self.data[self._Sentence_length] = Feature(
            mean=r2(self.token_count, self.sents), median=median(self.sentence_length_counter)
        )

        if not isinstance(self.blocks[0], (Token, Sentence)):
            scalar_list = [block.general.sents for block in self.blocks]
            self.data[self._Sentences].mean = mean(scalar_list)
            self.data[self._Sentences].median = median(scalar_list)

    def _set_text_features(self) -> None:
        blocks = [p for t in self.blocks for p in t.paragraphs] if isinstance(self.blocks[0], Text) else self.blocks
        token2paragraph = [b.general.token_count for b in blocks]
        sent2paragraph = [b.general.sents for b in blocks]
        paragraph_length = len(blocks)
        self.data[self._Paragraphs] = Feature(scalar=paragraph_length)
        self.data[self._Paragraph_length_word] = Feature(
            mean=r2(self.token_count, paragraph_length), median=median(token2paragraph)
        )
        self.data[self._Paragraph_length_sentence] = Feature(
            mean=r2(self.sents, paragraph_length), median=median(sent2paragraph)
        )