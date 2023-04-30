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
from typing import List

from swegram_main.config import KELLY_EN, KELLY_SV, ADVANCE_CEFR_LEVELS, WPM_SV
from swegram_main.data.tokens import Token
from swegram_main.data.sentences import Sentence
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.texts import Text
from swegram_main.lib.utils import mean, median, r2, merge_dicts_for_fields, get_sum_list_for_fields
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
    cefr_list = []
    wpm_sv_list = []
    kelly_dict = KELLY_EN if lang == "en" else KELLY_SV

    for token in tokens:
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
        

    return  sum(token_length_list), len(tokens), words, syllables, polysyllables, misspells, compounds, \
            _3sg_pron, neut_noun, s_verb, rel_pron, pres_verb, past_verb, sup_verb, pres_pc, past_pc, \
            advance_cefr, advance_noun_or_verb, 1, \
            freq_form_dict_upos, freq_norm_dict_upos, freq_lemma_dict_upos, \
            freq_form_dict_xpos, freq_norm_dict_xpos, freq_lemma_dict_xpos, \
            upos_dict, xpos_dict, word_dict, \
            Counter(token_length_list), Counter([len(tokens)]), Counter(cefr_list), Counter(wpm_sv_list), list(types)


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
    scalars = get_sum_list_for_fields(blocks, CountFeatures.SCALAR_FIELDS[:-1])  # sents is computed separately
    freqs = merge_dicts_for_fields(blocks, CountFeatures.FREQ_FIELDS)
    counters = _merge_counters(blocks, CountFeatures.COUNTER_FIELDS)
    types = _union(blocks, CountFeatures.UNION_FIELD)

    return *scalars, sents, *freqs, *counters, types


class CountFeatures:

    # Field Declaration
    SCALAR_FIELDS = [
        "chars", "token_count", "words", "syllables", "polysyllables", "misspells", "compounds",
        "_3sg_pron", "neut_noun", "s_verb", "rel_pron", "pres_verb", "past_verb", "sup_verb", "pres_pc", "past_pc",
        "advance_cefr", "advance_noun_or_verb",
        "sents",
    ]
    FREQ_FIELDS = [
        "freq_form_dict_upos", "freq_norm_dict_upos", "freq_lemma_dict_upos",
        "freq_form_dict_xpos", "freq_norm_dict_xpos", "freq_lemma_dict_xpos",
        "upos_dict", "xpos_dict", "word_dict"
    ]
    COUNTER_FIELDS = ["token_length_counter", "sentence_length_counter", "cefr_counter", "wpm_sv_counter"]
    UNION_FIELD = "types"
    FIELDS = [*SCALAR_FIELDS, *FREQ_FIELDS, *COUNTER_FIELDS, UNION_FIELD]

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
        self.feats = OrderedDict()
        self.average = OrderedDict()
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
            self.feats[feature_name] = getattr(self, attribute)
            if not isinstance(self.blocks[0], Token):
                scalar_list = [getattr(block.general, attribute) for block in self.blocks]
                self.average[feature_name] = {"mean": mean(scalar_list), "median": median(scalar_list)}
        self.average["Word length"] = {"mean": r2(self.chars, self.token_count), "median": median(self.token_length_counter)}

    def _set_paragraph_features(self) -> None:
        self.feats[self._Sentences] = self.sents
        self.feats[self._Sentence_length] = {
            "mean": r2(self.token_count, self.sents),
            "median": median(self.sentence_length_counter)
        }
        if not isinstance(self.blocks[0], (Token, Sentence)):
            scalar_list = [block.general.sents for block in self.blocks]
            self.average[self._Sentences] = {"mean": mean(scalar_list), "median": median(scalar_list)}

    def _set_text_features(self) -> None:
        blocks = [p for t in self.blocks for p in t.paragraphs] if isinstance(self.blocks[0], Text) else self.blocks
        token2paragraph = [b.general.token_count for b in blocks]
        sent2paragraph = [b.general.sents for b in blocks]
        paragraph_length = len(blocks)
        self.feats[self._Paragraphs] = paragraph_length
        self.average[self._Paragraph_length_word] = {
            "mean": r2(self.token_count, paragraph_length),
            "median": median(token2paragraph)
        }
        self.average[self._Paragraph_length_sentence] = {
            "mean": r2(self.sents, paragraph_length),
            "median": median(sent2paragraph)
        }
