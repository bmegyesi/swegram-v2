from typing import Any, Dict

from datetime import datetime
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.config import MAX_DAYS, DATE_FORMAT
from server.lib.fetch_data import fetch_data
from server.routers.database import get_db
from server.models import Text


router = APIRouter()


def remove_texts():
    """Delete text which is stored longer than one week"""
    current_time = datetime.now()
    print(f"Database cleanup {current_time}")
    db = next(get_db())
    text: Text
    for text in db.query(Text).all():
        saved_time = current_time - datetime.strptime(text.date, DATE_FORMAT)
        if saved_time.days > MAX_DAYS:
            print(f"To delete expired file {text.filename}.")
            print(f"Created time: {text.date}; size: {text._filesize}")
            db.delete(text)
            db.commit()


@router.get("/")
async def read_texts(db: Session = Depends(get_db)) -> JSONResponse:
    return JSONResponse([item.as_dict() for item in db.query(Text).all()])


@router.put("/{language}")
async def update_texts(
    language: str = Path(...), data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    texts = db.query(Text).filter(Text.language == language)
    return JSONResponse(fetch_data(metadata=data, texts=texts))
