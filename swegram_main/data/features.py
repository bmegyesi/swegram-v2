"""Feature class declaration"""

from dataclasses import dataclass
from typing import Optional, TypeVar, Dict, Union


F = TypeVar("F", int, float)


@dataclass
class Feature:
    scalar: Optional[F] = None
    mean: Optional[F] = None
    median: Optional[F] = None

    @property
    def json(self) -> Dict[str, Union[int, float]]:
        return {
            "scalar": self.scalar or "",
            "mean": self.mean or "",
            "median": self.median or ""
        }
