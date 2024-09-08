"""Task related models module

task is a text annotation job.
"""
import sys
from typing import Any, Dict, List, Union
from sqlalchemy import Column, Integer, String, Boolean, Sequence, ForeignKey, JSON, func, Enum
from sqlalchemy import Text as LONGTEXT
from sqlalchemy.ext.declarative import declarative_base


def _declarative_constructor(self, **kwargs) -> None:
    """Don't raise a TypeError for unknown attribute names."""
    cls_ = type(self)
    for k, v in kwargs.items():
        if not hasattr(cls_, k):
            continue
        setattr(self, k, v)


Base = declarative_base(constructor=_declarative_constructor)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, Sequence("task_id_seq"), primary_key=True, index=True)

    filename = Column(String(length=255))
    state = Column(Enum)  # ongoing, finished
    verdict = Column(Enum) # failed, passed
    start_time = None
    date = Column(String(length=225), default=func.now())
    content = Column(LONGTEXT, nullable=True)
    labels = Column(JSON, nullable=True)
    has_label = Column(Boolean, default=False)