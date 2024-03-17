from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.fetch_data import fetch_data
from server.routers.database import get_db
from server.models import Text


router = APIRouter()


@router.get("/")
async def read_texts(db: Session = Depends(get_db)) -> JSONResponse:
    return JSONResponse([item.as_dict() for item in  db.query(Text).all()])


@router.put("/{language}")
async def update_texts(
    language: str = Path(...), data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    texts = db.query(Text).filter( Text.language == language )
    return JSONResponse(fetch_data(metadata=data, texts=texts))
