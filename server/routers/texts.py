from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.fetch_data import fetch_data
from server.routers.database import get_db
from server.models import Text


router = APIRouter()


@router.get("/")
def read_texts(db: Session = Depends(get_db)) -> JSONResponse:
    return JSONResponse([item.as_dict() for item in  db.query(Text).all()])


@router.put("/")
def update_texts(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)) -> JSONResponse:
    texts = db.query(Text).all()
    return JSONResponse(fetch_data(metadata=data, texts=texts))
