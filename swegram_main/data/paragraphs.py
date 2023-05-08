from dataclasses import dataclass
from typing import Any, List, Optional

from swegram_main.data.sentences import Sentence


@dataclass
class Paragraph:

    text_id: str
    language: str
    sentences: List[Sentence]
    elements: Optional[str] = "sentences"
    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None
    morph: Optional[Any]                    = None
    lexical: Optional[Any]                  = None
    syntactic: Optional[Any]                = None

    def __str__(self):
        return " ".join([str(s) for s in self.sentences])
