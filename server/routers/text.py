from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.lib.load_data import parse_payload, run_swegram
from server.lib.fetch_current_sentences import fetch_current_sentences
from server.routers.database import get_db
from server.models import Text


router = APIRouter()


def _create_text(data, language, db):
    data = parse_payload(data)
    texts = run_swegram(language, **data)
    for text_data in texts:
        paragraphs = text_data["paragraphs"]
        del text_data["paragraphs"]
        text = Text(**text_data)
        try:
            db.add(text)
            db.commit()
            db.refresh(text)
            text.load_data(paragraphs, db)
        except Exception as err:
            db.rollback()
            raise Exception("Failed to create Text instance in the database.") from err


@router.get("/{text_id}")
async def read_text(text_id: int = Path(..., title="Text id"), db: Session = Depends(get_db)) -> JSONResponse:
    try:
        text = db.query(Text).get(ident=text_id)
        if not text:
            raise AttributeError
        return JSONResponse(text.as_dict())
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Text {text_id} not found.")


@router.get("/{text_id}/{page}/")
async def read_current_sentences(
    text_id: int = Path(..., title="Text id"),
    page: int = Path(..., title="Page"), db: Session = Depends(get_db)
) -> JSONResponse:
    return fetch_current_sentences(text_id=text_id, page=page, db=db)


@router.post("/{language}")
async def create_text(
    background_tasks: BackgroundTasks,
    language: str = Path(..., title="Language"),
    data: bytes = Body(...), db: Session = Depends(get_db)
) -> JSONResponse:
    # data = parse_payload(data)
    # texts = run_swegram(language, **data)
    # for text_data in texts:
    #     paragraphs = text_data["paragraphs"]
    #     del text_data["paragraphs"]
    #     text = Text(**text_data)
    #     try:
    #         db.add(text)
    #         db.commit()
    #         db.refresh(text)
    #         text.load_data(paragraphs, db)
    #     except Exception as err:
    #         db.rollback()
    #         raise Exception("Failed to create Text instance in the database.") from err
    background_tasks.add_task(_create_text, data, language, db)
    return JSONResponse({"success": "1", "text_stats_list": []})


@router.delete("/{text_id}")
async def delete_text(text_id: int = Path(..., title="Text id"), db: Session = Depends(get_db)) -> JSONResponse:
    try:
        text = db.query(Text).get(ident=text_id)
        db.delete(text)
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    return JSONResponse(text.as_dict())
