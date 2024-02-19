"""Fetch current sentences"""
from typing import Any, Dict

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.models import Text
from swegram_main.config import PAGE_SIZE

def fetch_current_sentences(text_id: int, page: int, db: Session) -> Dict[str, Any]:
    """The default size to show the sentence for visualization is 20"""

    data = {
      "current_sentences": [],
      "metadata": [],
      "total_items": 0,
      "page_size": PAGE_SIZE,
    }

    try:
        text = db.query(Text).get(ident=text_id)
        # sentences = db.query()
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    return JSONResponse(text.json())


# from django.http.response import JsonResponse
# from ..config import PAGE_SIZE
# from .helpers import eval_str
# from ..models import Text, TextStats, Sentence, Token
# from django.core.serializers import serialize
# import json

# def fetch_current_sentences(request, text_id, page):
#     """
#     The default size to show the sentences for visualisation is 20
#     """
#     data = {
#       'current_sentences': [],
#       'metadata': [],
#       'total_items': 0,
#       'page_size': PAGE_SIZE,
#     }

#     textStats = TextStats.objects.get(text_id=int(text_id))
#     text = Text.objects.get(stats=textStats)
#     sentences = Sentence.objects.filter(text=text).order_by('id')[(int(page)-1) * PAGE_SIZE:int(page) * PAGE_SIZE]
#     current_sentences = []
#     for sentence in sentences:
#         tokens = json.loads(
#           serialize('json', Token.objects.filter(sentence=sentence))
#         )
#         token_list = []
#         for t in tokens:
#             token = t['fields']
#             token['text_id'] = token['text_index']
#             token['token_id'] = token['token_index']
#             del token['text_index']
#             del token['token_index']
#             token_list.append(token)
#         current_sentences.append({'tokens':token_list})

#     data['current_sentences'] = current_sentences
#     data['metadata'] = list(eval_str(textStats.labels).items())
#     data['total_items'] = textStats.number_of_sentences
#     return JsonResponse(data)
