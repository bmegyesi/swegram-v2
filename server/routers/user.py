from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.routers.database import get_db
from server.models.user import User


router = APIRouter()


@router.post("/")
async def create_user(
    data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """Post user"""
    try:
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return JSONResponse({**data, "success": 1})
    except IntegrityError as err:
        return JSONResponse({**data, "success": 0, "error_msg": err})


@router.put("/")
async def validate_user(
    data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """Post states"""
    name = data["username"]
    user = db.query(User).get(ident=name)
    if not user:
        return JSONResponse({**data, "success": 0, "error_msg": f"Username {name} is not found."})
    if data["password"] != user.password:
        return JSONResponse({**data, "success": 0, "error_msg": "Invalid username or password"})
    return JSONResponse(data)


@router.put("/reset")
async def reset_password(
    data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """Post states"""
    name = data["username"]
    user = db.query(User).get(ident=name)
    if not user:
        return JSONResponse({**data, "success": 0, "error_msg": f"Username {name} is not found."})
    if data["password"] != user.password:
        return JSONResponse({**data, "success": 0, "error_msg": "Invalid username or password"})
    # reset password
    return JSONResponse(data)
