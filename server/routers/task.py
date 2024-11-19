from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.exceptions import ServerError
from server.lib.fetch_current_sentences import fetch_current_sentences
from server.lib.load_data import parse_payload, run_swegram
from server.routers.database import get_db
from server.models import Text, Task


router = APIRouter()


class TaskNotFoundError(Exception):
    """Task not found error"""


@router.get("/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    try:
        task = db.query(Task).get(task_id)
        if not task:
            raise TaskNotFoundError
        return JSONResponse(task.as_dict())
    except TaskNotFoundError as err:
         raise HTTPException(status_code=404, detail=f"Task {task_id} not found.") from err


@router.post("/create")
async def create_task(data = Body(...), db: Session = Depends(get_db)) -> Dict[str, int]:
    text_id = data["text_id"]
    new_task = Task(text_id=text_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"task_id": new_task.id}


@router.put("/{task_id}")
async def update_task(task_id: int = Path(...), data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    try:
        task = db.query(Task).get(indent=task_id)
        if not task:
            raise TaskNotFoundError
        for key, value in data.items():
            setattr(task, key, value)
        db.commit()
        return JSONResponse(task.as_dict())
    except TaskNotFoundError as err:
         raise HTTPException(status_code=404, detail=f"Task {task_id} not found.") from err
