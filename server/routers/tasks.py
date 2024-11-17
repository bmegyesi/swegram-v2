from copy import copy
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.routers.database import get_db
from server.models import Task


router = APIRouter()


@router.get("/")
async def get_tasks(db: Session = Depends(get_db)) -> JSONResponse:
    """return all tasks"""
    return JSONResponse([item.as_dict() for item in db.query(Task).all()])


@router.get("/latest")
async def get_latest_tasks(db: Session = Depends(get_db)) -> JSONResponse:
    """return latest 10 tasks"""
    ...
