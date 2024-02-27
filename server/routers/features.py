from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.routers.database import get_db
from server.lib.fetch_features import get_features, get_features_for_elements

router = APIRouter()


@router.post("/{element}/{index}")
def read_features_for_one_element(
    element: str = Path(..., title="Element"),
    index: int = Path(..., title="Index"),
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    return JSONResponse(get_features(element, index, data, db))


@router.post("/{elements}")
def read_features_for_elements(
    elements: str = Path(..., title="Element"),
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    return JSONResponse(get_features_for_elements(elements, data, db))
