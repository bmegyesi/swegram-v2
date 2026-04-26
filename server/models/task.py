from dataclasses import dataclass
from sqlalchemy import Column, Integer, Sequence, String, ForeignKey, func
from sqlalchemy.orm import relationship

from server.database.handler import Base
from server.models.attrs import Verdict, State


@dataclass
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, Sequence("task_id_seq"), primary_key=True, index=True, autoincrement=True)
    created_at = Column(String(255), nullable=False, default=func.now())
    state = Column(Integer, nullable=False, default=State.CREATED)
    verdict = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    job = relationship("Job", back_populates="tasks")

    def __repr__(self):
        return self.name
