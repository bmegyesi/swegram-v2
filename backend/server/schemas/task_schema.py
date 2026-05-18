from typing import Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    job_id: int
    state: int = 0
    verdict: Optional[int] = None


class TaskUpdate(BaseModel):
    state: Optional[int] = None
    verdict: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    job_id: int
    state: int
    verdict: Optional[int] = None

    class Config:
        from_attributes = True
