"""job module"""
from dataclasses import dataclass
from sqlalchemy import Column, Integer, Sequence, String, func
from sqlalchemy.orm import relationship
from server.database.handler import Base
from server.models.attrs import Verdict, State


@dataclass
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, Sequence("job_id_seq"), primary_key=True, index=True, autoincrement=True)
    language = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    created_at = Column(String(255), nullable=False, default=func.now())
    state = Column(Integer, nullable=False, default=State.CREATED)
    verdict = Column(Integer, nullable=True)
    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return f"Text-Annotation-{self.filename}"
