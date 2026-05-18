from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:  # pylint: disable=too-many-instance-attributes
    """Data structure for token instance"""
    text_index: str
    token_index: str
    form: str
    norm: str
    lemma: str
    upos: str
    xpos: str
    feats: str
    ufeats: Optional[str]
    head: str
    deprel: str
    deps: str
    misc: str
    path: Optional[str]       = None # The path between the current token and the root.
    dep_length: Optional[int] = None # The depth between the current token and the root.
    length: Optional[int]     = None
    highlight: Optional[bool] = None

    def __str__(self):
        return self.form
