from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.routers.database import get_db
from server.lib.fetch_features import get_features, get_overview_features_for_level


router = APIRouter()


@router.post("/{element}/{index}")
async def read_features_for_one_element(
    element: str = Path(..., title="Element"),
    index: int = Path(..., title="Index"),
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    return JSONResponse(get_features(element, index, data, db))


@router.post("/{level}")
async def read_features_for_elements(
    level: str = Path(..., title="Element"),
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    return JSONResponse(get_overview_features_for_level(level, data, db))
