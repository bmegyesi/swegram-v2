import os
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from server.routers.database import get_db
from server.lib.download import download_texts as _download_texts
from server.lib.download import download_statistics as _download_statistics


router = APIRouter()


@router.post("/texts/")
async def download_texts(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)) -> FileResponse:
    return await _download_texts(data, db)


@router.post("/statistics/")
async def download_statistics(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)) -> FileResponse:
    return await _download_statistics(data, db)


@router.delete("/file/")
async def delete_file(data: Dict[str, str] = Body(...)) -> HTMLResponse:
    os.unlink(data["name"])
    return HTMLResponse("Success")
