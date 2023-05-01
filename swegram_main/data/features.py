"""Feature class declaration"""

from dataclasses import dataclass
from typing import Optional, TypeVar


F = TypeVar("F", int, float)


@dataclass
class Feature:
    scalar: Optional[F] = None
    mean: Optional[F] = None
    median: Optional[F] = None
