from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.database.handler import get_db
from server.lib.fetch_frequencies import fetch_frequencies


router = APIRouter()


@router.post("/{category}/{tagset}/")
async def fetch_word_and_tag(
    category: str = Path(..., title="Category"),
    tagset: str = Path(..., title="Tagset"),
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    return JSONResponse(fetch_frequencies(category, tagset, data, db))
