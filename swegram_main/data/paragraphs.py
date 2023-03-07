from dataclasses import dataclass
from typing import Any, List, Optional

from swegram_main.data.sentences import Sentence


@dataclass
class Paragraph:

    text_id: str
    sentences: List[Sentence]

    # statistics
    general: Optional[Any]                  = None
    readability: Optional[Any]              = None

    morphological: Optional[Any]            = None
    morphological_average: Optional[Any]    = None

    lexical: Optional[Any]                  = None
    lexical_average: Optional[Any]          = None

    syntactic: Optional[Any]                = None
    syntactic_average: Optional[Any]        = None

    def __str__(self):
        return ' '.join([str(s) for s in self.sentences])
