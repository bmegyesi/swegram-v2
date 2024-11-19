from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.exceptions import ServerError
from server.lib.fetch_current_sentences import fetch_current_sentences
from server.lib.load_data import parse_payload, run_swegram
from server.routers.database import get_db
from server.models import Text, TaskGroup


router = APIRouter()


class TaskNotFoundError(Exception):
    """Task not found error"""


@router.get("/{task_id}")
async def get_taskgroup(taskgroup_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    try:
        task = db.query(TaskGroup).get(taskgroup_id)
        if not task:
            raise TaskNotFoundError
        return JSONResponse(task.as_dict())
    except TaskNotFoundError as err:
         raise HTTPException(status_code=404, detail=f"Task Group {taskgroup_id} not found.") from err


@router.post("/create")
async def create_taskgroup(db: Session = Depends(get_db)) -> Dict[str, int]:
    new_taskgroup = TaskGroup()
    db.add(new_taskgroup)
    db.commit()
    db.refresh(new_taskgroup)
    return {"taskgroup_id": new_taskgroup.id}


@router.put("/{task_id}")
async def update_taskgroup(taskgroup_id: int = Path(...), data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    try:
        taskgroup = db.query(TaskGroup).get(taskgroup_id)
        if not taskgroup:
            raise TaskNotFoundError
        for key, value in data.items():
            setattr(taskgroup, key, value)
        db.commit()
        return JSONResponse(taskgroup.as_dict())
    except TaskNotFoundError as err:
         raise HTTPException(status_code=404, detail=f"Task {taskgroup_id} not found.") from err
