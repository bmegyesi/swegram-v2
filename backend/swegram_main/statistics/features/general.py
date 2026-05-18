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
from typing import List, Tuple, Any

from swegram_main.config import (
    KELLY_EN, KELLY_SV, ADVANCE_CEFR_LEVELS, WPM_SV,
    MODIFIER_DEPREL_LABELS, SUBORDINATION_DEPREL_LABELS,
    LONG_ARC_THRESHOLD
)
from swegram_main.data.features import Feature
from swegram_main.data.paragraphs import Paragraph
from swegram_main.data.sentences import Sentence
from swegram_main.data.texts import Text, Corpus
from swegram_main.data.tokens import Token
from swegram_main.lib.utils import (
    get_path, get_child_nodes, is_a_ud_tree,
    merge_digits_for_fields,
    mean, median, r2, merge_dicts_for_fields
)
from swegram_main.statistics.statistic_types import B, S


ENGLISH_VOWELS = "aoueiy"
SWEDISH_VOWELS = f"{ENGLISH_VOWELS}åöä"


class SerializationError(Exception):
    """Serialization Error"""


class SyntaticAnnotationParsingError(Exception):
    """Syntatic Annnotation Parsing Error"""


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


def _serialize_tokens(tokens: List[Token], lang: str) -> S:  # pylint: disable=too-many-locals, too-many-branches, too-many-statements

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

        if norm != "_":
            types.add(norm)
        else:
            types.add(form)

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
                if upos in {"NOUN", "VERB"}:
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
                raise SyntaticAnnotationParsingError(
                    f"Token head index points to itself: index, {index}, heads, {heads}"
                )
            if token.deprel.startswith(tuple(MODIFIER_DEPREL_LABELS)):
                if heads[index] < index:
                    post_modifier += 1
                elif heads[index] > index:
                    pre_modifier += 1
                else:
                    raise SyntaticAnnotationParsingError(
                        f"Token head index points to itself: index, {index}, heads, {heads}"
                    )
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
            for key, value in getattr(block, field).items():
                counter[key] += value
        counters.append(counter)
    return counters


def _union(blocks: List[B], field: str) -> List[str]:
    union = set()
    for block in blocks:
        union = union.union(getattr(block, field))
    return list(union)


def _serialize(blocks: List[B], lang: str) -> S:
    if isinstance(blocks[0], Token):
        return _serialize_tokens(blocks, lang)
    if isinstance(blocks[0], Sentence):
        sents = len(blocks)
    elif isinstance(blocks[0], (Paragraph, Text)):
        sents = sum(block.sents for block in blocks)
    else:
        raise SerializationError(f"Unknown block type: {type(blocks[0])}")
    scalars = merge_digits_for_fields(blocks, CountFeatures.SCALAR_FIELDS[:-1])  # sents is computed separately
    freqs = merge_dicts_for_fields(blocks, CountFeatures.FREQ_FIELDS)
    counters = _merge_counters(blocks, CountFeatures.COUNTER_FIELDS)
    types = _union(blocks, CountFeatures.UNION_FIELD)
    depth_list = [t for block in blocks for t in getattr(block, CountFeatures.LIST_FIELD)]

    return *scalars, sents, *freqs, *counters, types, depth_list


class CountFeatures:

    ASPECT = "general"

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
    SENTENCE_FEATURES = [
        ("Token-count", "token_count"),
        ("Type-count", "type_count"),
        ("Spelling errors", "misspells"),
        ("Compound errors", "compounds"),
        # ("Word length")  # Word length is computed separately
    ]

    _Sentences, _Sentence_length = "Sentences", "Sentence length (n words)"
    PARAGRAPH_FEATURES = [_Sentences, _Sentence_length]

    _Paragraphs, _Paragraph_length_word = "Paragraphs", "Paragraph length (n words)"
    _Paragraph_length_sentence = "Paragraph length (n sentences)"
    TEXT_FEATURES = [_Paragraphs, _Paragraph_length_word, _Paragraph_length_sentence]
 

    def load_instance(self, instance: B, lang: str) -> B:
        instance = update_instance_with_metadata(instance, lang, getattr(instance, instance.elements))
        instance.general = OrderedDict()  # initialize general orderedDict instance
        if isinstance(instance, (Sentence, Paragraph, Text, Corpus)):
            for feature_name, attribute in self.SENTENCE_FEATURES:
                if isinstance(instance, Sentence):
                    instance.general[feature_name] = Feature(scalar=getattr(instance, attribute))
                else:
                    scalar_list = [getattr(element, attribute) for element in getattr(instance, instance.elements)]
                    instance.general[feature_name] = Feature(
                        scalar=getattr(instance, attribute),
                        mean=mean(scalar_list), median=median(scalar_list)
                    )
            instance.general["Word length"] = Feature(
                scalar=instance.chars,
                mean=r2(instance.chars, instance.token_count), median=median(instance.token_length_counter)
            )
        if isinstance(instance, (Paragraph, Text, Corpus)):
            sents_scalar_list = [b.sents for b in getattr(instance, instance.elements)]
            instance.general[self._Sentences] = Feature(
                scalar=sum(sents_scalar_list),
                mean=mean(sents_scalar_list), median=median(sents_scalar_list)
            )
            instance.general[self._Sentence_length] = Feature(
                scalar=instance.token_count,
                mean=r2(instance.token_count, instance.sents), median=median(instance.sentence_length_counter)
            )
        if isinstance(instance, (Text, Corpus)):
            if isinstance(instance, Text):
                paragraphs = instance.paragraphs
            else:
                paragraphs = [p for t in instance.texts for p in t.paragraphs]

            token2paragraph = [p.token_count for p in paragraphs]
            sents2paragraph = [p.sents for p in paragraphs]
            paragraph_length = len(paragraphs)
            instance.general[self._Paragraphs] = Feature(scalar=paragraph_length)
            instance.general[self._Paragraph_length_word] = Feature(
                mean=r2(instance.token_count, paragraph_length), median=median(token2paragraph)
            )
            instance.general[self._Paragraph_length_sentence] = Feature(
                mean=r2(instance.sents, paragraph_length), median=median(sents2paragraph)
            )

        return instance


def update_instance_with_metadata(instance: B, lang: str, components: List[Any]) -> B:
    for key, value in zip(CountFeatures.FIELDS, _serialize(components, lang)):
        setattr(instance, key, value)
    setattr(instance, "type_count", len(instance.types))
    return instance
