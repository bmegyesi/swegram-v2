"""job module"""
from dataclasses import dataclass
from sqlalchemy import Column, ForeignKey, Integer, Sequence, String, func
from sqlalchemy.orm import relationship
from server.database.handler import Base
from server.models.attrs import State


@dataclass
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, Sequence("job_id_seq"), primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    language = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    job_name = Column(String(255), nullable=False)
    created_at = Column(String(255), nullable=False, default=func.now())  # pylint: disable=not-callable
    updated_at = Column(String(255), nullable=False, server_default=func.now(), onupdate=func.now())  # pylint: disable=not-callable
    state = Column(Integer, nullable=False, default=State.CREATED)
    verdict = Column(Integer, nullable=True)

    # self-referential relationships
    parent = relationship("Job", remote_side=[id], back_populates="children")
    children = relationship("Job", back_populates="parent", cascade="all, delete-orphan")

    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return f"Text-Annotation-{self.filename}"
