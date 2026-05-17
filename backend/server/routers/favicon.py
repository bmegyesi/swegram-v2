from fastapi import APIRouter
from fastapi.responses import FileResponse


favicon_path = "fastapi.svg"
router = APIRouter()


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
