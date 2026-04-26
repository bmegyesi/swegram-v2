from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from server.database.handler import TaskDatabaseHandler
from server.models.task import Task
from server.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(TaskDatabaseHandler.get_db)):
    db_task = Task(state=task.state, verdict=task.verdict, name=task.name, job_id=task.job_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(TaskDatabaseHandler.get_db)):
    return db.query(Task).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(TaskDatabaseHandler.get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(TaskDatabaseHandler.get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.state is not None:
        db_task.state = task.state
    if task.verdict is not None:
        db_task.verdict = task.verdict
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(TaskDatabaseHandler.get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}
