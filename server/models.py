"""data models module"""
import sys
from typing import Any, Dict, List, Union
from sqlalchemy import Column, Integer, String, Boolean, Sequence, ForeignKey, JSON, func, Enum
from sqlalchemy import Text as LONGTEXT
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, Session

from server.lib.load_data import get_size_and_format


def _declarative_constructor(self, **kwargs) -> None:
    """Don't raise a TypeError for unknown attribute names."""
    cls_ = type(self)
    for k in kwargs:
        if not hasattr(cls_, k):
            continue
        setattr(self, k, kwargs[k])

Base = declarative_base(constructor=_declarative_constructor)


##############################################
class SharedMethodMixin:

    @declared_attr
    def __tablename__(cls):
        return None

    @declared_attr
    def id(cls):
        return None

    def as_dict(self) -> Dict[str, Any]:
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }


##############################################
class SharedAttributeMixin:

    # Metadata for computation helper
    language = Column(Enum("sv", "en"))
    uuid = Column(String(length=255))
    elements = Column(String(length=255), nullable=True)
    # JSON Aspect block
    general = Column(JSON, nullable=True)
    lexical = Column(JSON, nullable=True)
    morph = Column(JSON, nullable=True)
    readability = Column(JSON, nullable=True)
    syntactic = Column(JSON, nullable=True)

class TextAttributeMixin:

    ## integer block
    _3sg_pron = Column(Integer, nullable=True)
    advance_cefr = Column(Integer, nullable=True)
    advance_noun_or_verb = Column(Integer, nullable=True)
    chars = Column(Integer, nullable=True)
    compounds = Column(Integer, nullable=True)
    left_arcs = Column(Integer, nullable=True)
    long_arcs = Column(Integer, nullable=True)
    misspells = Column(Integer, nullable=True)
    neut_noun = Column(Integer, nullable=True)
    past_pc = Column(Integer, nullable=True)
    past_verb = Column(Integer, nullable=True)
    polysyllables = Column(Integer, nullable=True)
    post_modifier = Column(Integer, nullable=True)
    pre_modifier = Column(Integer, nullable=True)
    preposition_nodes = Column(Integer, nullable=True)
    pres_pc = Column(Integer, nullable=True)
    pres_verb = Column(Integer, nullable=True)
    rel_pron = Column(Integer, nullable=True)
    relative_clause_nodes = Column(Integer, nullable=True)
    right_arcs = Column(Integer, nullable=True)
    s_verb = Column(Integer, nullable=True)
    sents = Column(Integer, nullable=True)
    subordinate_nodes = Column(Integer, nullable=True)
    sup_verb = Column(Integer, nullable=True)
    syllables = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    type_count = Column(Integer, nullable=True)
    words = Column(Integer, nullable=True)
    # JSON counter block
    cefr_counter = Column(JSON, nullable=True)  # Counter({'1': 105, '2': 23, '3': 8, '4': 8, '6': 4, '5': 3})
    sentence_length_counter = Column(JSON, nullable=True)
    token_length_counter = Column(JSON, nullable=True)
    wpm_sv_counter = Column(JSON, nullable=True)

    # JSON defaultdict block
    freq_form_dict_upos = Column(JSON, nullable=True)
    freq_form_dict_xpos = Column(JSON, nullable=True)
    freq_lemma_dict_upos = Column(JSON, nullable=True)
    freq_lemma_dict_xpos = Column(JSON, nullable=True)
    freq_norm_dict_upos = Column(JSON, nullable=True)
    freq_norm_dict_xpos = Column(JSON, nullable=True)
    upos_dict = Column(JSON, nullable=True)
    word_dict = Column(JSON, nullable=True)
    xpos_dict = Column(JSON, nullable=True)

    # Array block
    depth_list = Column(JSON, nullable=True)
    types = Column(JSON, nullable=True)


class Text(Base, SharedMethodMixin, SharedAttributeMixin, TextAttributeMixin):
    __tablename__ = "texts"

    id = Column(Integer, Sequence("text_id_seq"), primary_key=True, index=True)

    filename = Column(String(length=255))
    activated = Column(Boolean, default=False)
    date = Column(String(length=225), default=func.now())
    content = Column(LONGTEXT, nullable=True)
    labels = Column(JSON, nullable=True)
    has_label = Column(Boolean, default=False)
    _filesize = Column(Integer, nullable=True)

    tokenized = Column(Boolean, default=True)
    normalized = Column(Boolean, default=False)
    tagged = Column(Boolean, default=False)
    parsed = Column(Boolean, default=False)

    paragraphs = relationship("Paragraph", back_populates="text", cascade="all, delete-orphan")

    @property
    def filesize(self) -> str:
        if self._filesize:
            return get_size_and_format(self._filesize)
        if self.content:
            return get_size_and_format(sys.getsizeof(self.content))
        return "0"


    def short(self) -> Dict[str, Any]:
        return {**{
            c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in [
                "uuid", "language", "filename", "labels", "activated",
                "tokenized", "normalized", "tagged", "parsed"
            ]}, **{
                "number_of_paragraphs": len(self.paragraphs),
                "number_of_sentences": self.sents,
                "date": str(self.date)
            }
        }

    def header(self):
        TAGS = [
            "text_id", "token_id", "form", "norm", "lemma", "upos",
            "xpos", "feats", "ufeats", "head", "deprel", "deps", "misc"
        ]
        if self.language == "en":
            TAGS.remove("ufeats")
        return TAGS

    def load_data(self, paragraphs: List[Dict[str, Any]], db: Session) -> None:

        for p_index, paragraph in enumerate(paragraphs, 1):
            sentences = paragraph["sentences"]
            del paragraph["sentences"]
            paragraph_instance = Paragraph(text_id=self.id, index=str(p_index), **paragraph)
            db.add(paragraph_instance)
            db.commit()
            db.refresh(paragraph_instance)

            for s_index, sentence in enumerate(sentences, 1):
                tokens = sentence["tokens"]
                del sentence["tokens"]
                sentence_instance = Sentence(paragraph_id=paragraph_instance.id, index=str(s_index), **sentence)
                db.add(sentence_instance)
                db.commit()
                db.refresh(sentence_instance)

                for t_index, token in enumerate(tokens, 1):
                    if self.parsed:
                        token["dep_length"] = len(sentence["depth_list"][t_index-1]) - 1
                        token["path"] = " -> ".join(
                            [tokens[i-1]["form"] if i else "ROOT" for i in sentence["depth_list"][t_index-1]]
                        )
                    token["length"] = len(token["form"])
                    token["text_id"] = token["text_index"]
                    token["token_id"] = token["index"]
                    del token["text_index"]
                    del token["index"]
                    token["normalized"] = self.normalized
                    token_instance = Token(sentence_id=sentence_instance.id, **token)
                    db.add(token_instance)
        db.commit()

    def __str__(self) -> str:
        return "\n".join([str(paragraph) for paragraph in self.paragraphs])


class Paragraph(Base, SharedMethodMixin, SharedAttributeMixin):
    __tablename__ = "paragraphs"

    id = Column(Integer, Sequence("paragraph_id_seq"), primary_key=True, index=True)
    index = Column(String(255))

    sentences = relationship("Sentence", back_populates="paragraph", cascade="all, delete-orphan")

    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"))
    text = relationship("Text", back_populates="paragraphs")

    def __str__(self) -> str:
        return " ".join([str(sentence) for sentence in self.sentences])


class Sentence(Base, SharedMethodMixin, SharedAttributeMixin):
    __tablename__ = "sentences"

    id = Column(Integer, Sequence("sentence_id_seq"), primary_key=True, index=True)
    index = Column(String(255))
    ud_tree = Column(Boolean, nullable=True)

    tokens = relationship("Token", back_populates="sentence", cascade="all, delete-orphan")

    paragraph_id = Column(Integer, ForeignKey("paragraphs.id", ondelete="CASCADE"))
    paragraph = relationship("Paragraph", back_populates="sentences")

    def serialize_tokens(self):
        return [token.as_dict() for token in self.tokens]

    def __str__(self) -> str:
        return " ".join([str(token) for token in self.tokens])


class Token(Base, SharedMethodMixin):
    __tablename__ = "tokens"

    id = Column(Integer, Sequence("token_id_seq"), primary_key=True, index=True)

    compound_originals = Column(Boolean, default=False)
    normalized = Column(Boolean, default=False)
    token_id = Column(String(255))
    text_id = Column(String(255))

    form = Column(String(length=255), default="_")
    norm = Column(String(length=255), default="_")
    lemma = Column(String(length=255), default="_")
    upos = Column(String(length=255), default="_")
    xpos = Column(String(length=255), default="_")
    feats = Column(String(length=255), default="_")
    ufeats = Column(String(length=255), default="_")
    head = Column(String(length=255), default="_")
    deprel = Column(String(length=255), default="_")
    deps = Column(String(length=255), default="_")
    misc = Column(String(length=255), default="_")

    path = Column(String(length=1024), default="")
    highlight = Column(Boolean, default=False)

    length = Column(Integer, nullable=True)
    dep_length = Column(Integer, nullable=True)

    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"))
    sentence = relationship("Sentence", back_populates="tokens")

    def __str__(self) -> str:
        return self.form
    
    def conll(self, language: str, to_string: bool = True) -> Union[str, List[str]]:
        # language = self.sentence.paragraph.text.language
        feats = self.feats if language == "en" else f"{self.feats}\t{self.ufeats}"
        fields =[
            self.text_id, self.token_id, self.form, self.norm, self.lemma,
            self.upos, self.xpos, feats, self.head, self.deprel, self.deps, self.misc
        ]
        if to_string:
            return "\t".join(fields)
        return fields
