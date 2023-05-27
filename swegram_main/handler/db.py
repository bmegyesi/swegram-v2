"""loading data from file into database

"""
import json
from pathlib import Path
from typing import Dict

from swegram_main.handler.handler import load_text
from swegram_main.data.texts import Text
from swegram_main.models import TextModel, TextStat, ParagraphModel, SentenceModel, TokenModel


CONLLU_TAGS = {
    "en": "text_index token_index form norm lemma upos xpos feats head deprel deps misc",
    "sv": "text_index token_index form norm lemma upos xpos feats ufeats head deprel deps misc"
}


class TextLoadHandler:

    def __init__(self, language: str, filepath: Path, labels: Dict[str, str] = {}) -> None:
        self.language = language
        self.filepath = filepath
        self.labels = labels

    def load(self):
        text = load_text(
            language=self.language,
            filepath=self.filepath,
            labels=self.labels
        )
        load_text2db(text)

    def update(self):
        ...

    def delete(self, text_id):
        ...


def load_text2db(text: Text):
    """
    state instance: {
        "tokenized": True,
        "normalized": True,
        "tagged": True,
        "parsed": True
    }
    """
    text_stat_instance = TextStat.objects.create(
        text_id                 = text.id,
        language                = text.language,
        filename                = text.filename,
        filesize                = text.filesize,
        states                  = json.dumps(text.states), # if text is tokenized, normalized, tagged, parsed
        labels                  = json.dumps(text.labels),
        number_of_paragraphs    = len(text.paragraphs),
        number_of_sentences     = len(text.sentences)
    )
    text_instance = TextModel.objects.create(
        stats                   = text_stat_instance,
        general                 = json.dumps(text.general),
        readability             = json.dumps(text.readability),
        morph                   = json.dumps(text.morph)             if text.tagged else None,
        morph_lexical           = json.dumps(text.morph_average)     if text.tagged else None,
        lexical                 = json.dumps(text.lexical)           if text.tagged else None,
        lexical_average         = json.dumps(text.lexical_average)   if text.tagged else None,
        syntactic               = json.dumps(text.syntactic)         if text.parsed else None,
        syntactic_average       = json.dumps(text.syntactic_average) if text.parsed else None,
        content                 = "\n".join([str(p) for p in text.paragraphs])
    )
    for paragraph in text.paragraphs:
        paragraph_instance = ParagraphModel.objects.create(
            text                = text_instance,
            general             = json.dumps(paragraph.general),
            readability         = json.dumps(paragraph.readability),
            morph               = json.dumps(paragraph.morph)             if text.tagged else None,
            morph_average       = json.dumps(paragraph.morph_average)     if text.tagged else None,
            lexical             = json.dumps(paragraph.lexical)           if text.tagged else None,
            lexical_average     = json.dumps(paragraph.lexical_average)   if text.tagged else None,
            syntactic           = json.dumps(paragraph.syntactic)         if text.parsed else None,
            syntactic_average   = json.dumps(paragraph.syntactic_average) if text.parsed else None,
        )
        for sentence in paragraph.sentences:
            sentence_instance = SentenceModel.objects.create(
                text            = text,
                paragraph       = paragraph_instance,
                text_index      = sentence.text_id,
                types           = json.dumps(sentence.types),
                ud_tree         = True if sentence.syntactic else False,
                general         = json.dumps(sentence.general),
                readbility      = json.dumps(sentence.readability),
                morph           = json.dumps(sentence.morph)            if text.tagged else None,
                lexical         = json.dumps(sentence.lexical)          if text.tagged else None,
                syntactic       = json.dumps(sentence.syntactic)        if text.parsed else None,
                content         = str(sentence)
            )
            for token in sentence.tokens:
                token_instance = TokenModel.objects.create(
                    sentence          = sentence_instance,
                    compoud_originals = token.compound_originals,
                    normalized        = token.normalized,
                    token_index       = token.token_id,
                    text_index        = token.text_id,
                    form              = token.form,
                    norm              = token.norm,
                    lemma             = token.lemma,
                    upos              = token.upos,
                    xpos              = token.xpos,
                    feats             = token.feats,
                    ufeats            = token.ufeats,
                    head              = token.head,
                    deprel            = token.deprel,
                    misc              = token.misc,
                    path              = token.path,
                    length            = token.length,
                    dep_length        = token.dep_length
                )
                token_instance.save()
