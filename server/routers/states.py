from copy import copy
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.fetch_features import post_states as _post_states
from server.routers.database import get_db
from server.models import Text


router = APIRouter()


@router.put("/")
async def update_states(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)) -> JSONResponse:
    """Update states"""
    text_states = data["textStates"]
    for _id, status in copy(text_states).items():
        text = db.query(Text).get(int(_id))
        if text:
            text.activated = status
        else:
            del text_states[_id]
    db.commit()
    return JSONResponse(text_states)


@router.post("/")
async def post_states(
    data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """Post states"""
    return JSONResponse(_post_states(data, db))
