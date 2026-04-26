from pydantic import BaseModel
from typing import List, Optional

from server.schemas.task_schema import TaskResponse


class JobCreate(BaseModel):
    language: str
    filename: str
    state: int
    verdict: Optional[int] = None


class JobUpdate(BaseModel):
    state: Optional[int] = None
    verdict: Optional[int] = None


class JobResponse(BaseModel):
    id: int
    language: str
    filename: str
    created_at: str
    state: Optional[int] = None
    verdict: Optional[int] = None
    tasks: Optional[List[TaskResponse]] = None

    class Config:
        from_attributes = True
