"""Fetch current sentences"""
from typing import Any, Dict

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.models import Text, Sentence
from swegram_main.config import PAGE_SIZE


def fetch_current_sentences(text_id: int, page: int, db: Session) -> Dict[str, Any]:
    """The default size to show the sentence for visualization is 20"""

    try:
        text = db.query(Text).get(ident=text_id)
        sentences = db.query(Sentence) \
                      .filter(Sentence.uuid == text.uuid) \
                      .order_by(Sentence.id)[(int(page)-1) * PAGE_SIZE:int(page) * PAGE_SIZE]

        return JSONResponse({
            "current_sentences": [{"tokens": sentence.serialize_tokens()} for sentence in sentences],
            "metadata": text.labels.items() if text.labels else [],
            "total_items": text.sents,
            "page_size": PAGE_SIZE
        })
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
