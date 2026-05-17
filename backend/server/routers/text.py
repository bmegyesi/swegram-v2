from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.database.handler import DatabaseHandler
from server.lib.exceptions import ServerError
from server.lib.fetch_current_sentences import fetch_current_sentences
from server.lib.load_data import parse_payload, run_swegram
from server.models import Text


router = APIRouter()


def _create_text(data, language):
    data = parse_payload(data)
    try:
        run_swegram(language, **data)
    except Exception as err:
        raise ServerError("Failed to create Text instance in the database.") from err


@router.get("/{text_id}")
async def read_text(text_id: int = Path(..., title="Text id"), db: Session = Depends(DatabaseHandler.get_db)) -> JSONResponse:
    try:
        text = db.query(Text).get(ident=text_id)
        if not text:
            raise AttributeError
        return JSONResponse(text.as_dict())
    except AttributeError as err:
        raise HTTPException(status_code=404, detail=f"Text {text_id} not found.") from err


@router.get("/{text_id}/{page}/")
async def read_current_sentences(
    text_id: int = Path(..., title="Text id"),
    page: int = Path(..., title="Page"), db: Session = Depends(DatabaseHandler.get_db)
) -> JSONResponse:
    return fetch_current_sentences(text_id=text_id, page=page, db=db)


@router.post("/{language}")
async def create_text(
    background_tasks: BackgroundTasks,
    language: str = Path(..., title="Language"),
    data: bytes = Body(...), 
) -> JSONResponse:
    background_tasks.add_task(_create_text, data, language)
    return JSONResponse({"success": "1", "text_stats_list": []})


@router.delete("/{text_id}")
async def delete_text(text_id: int = Path(..., title="Text id"), db: Session = Depends(DatabaseHandler.get_db)) -> JSONResponse:

    text = db.query(Text).get(ident=text_id)
    db.delete(text)
    db.commit()
    return JSONResponse(text.as_dict())
