"""
The module of built-in api of get_text_states
"""
import json
import logging
import operator
import tempfile
from functools import reduce

from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from swegram_main.api.helpers.helper import (
  get_text_helper, 
  search_text_helper,
  update_text_helper,
  download_text_wrapper,
  download_stats_wrapper
)
from swegram_main.models import TextStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@require_http_methods(["GET", "PUT"])
def get_text_states(request):
    """
    Return text states in the database
    """
    return JsonResponse(get_text_helper(), safe=False)


@ensure_csrf_cookie
@require_http_methods(["PUT"])
def fetch_text_states(request):
    """update text states"""
    return JsonResponse(update_text_helper(request), safe=False)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def search_texts(_, query: str):
    """
    API to search text given the query
    """
    logger.info(f"Search texts given query: {query}")
    return JsonResponse(search_text_helper(query), safe=False)


@ensure_csrf_cookie
@require_http_methods(["PUT"])
def update_text(request):
    """
    API to update text states
    """
    _text_states = json.loads(request.body)['textStates']
    text_states = {int(key): value for key, value in _text_states.items()}
    matched_texts = TextStats.objects.filter(
      reduce(
        operator.or_, 
        (
          Q(text_id__exact=x) for x in text_states.keys()
        )
      )
    )
    for text in matched_texts:
        text.activated = text_states.get(text.text_id)
        text.save()
    return JsonResponse(text_states, safe=False)


@ensure_csrf_cookie
@require_http_methods(["DELETE"])
def delete_text(_, text_id):
    try:
        TextStats.objects.get(text_id=int(text_id)).delete()
        return JsonResponse({"sucess": "Successfully deleted!"})
    except Exception as err:
        return JsonResponse({"failure": f"Deletion failed: {str(err)}"})


@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_text(_, text_id):
    try:
        text = TextStats.objects.get(text_id=int(text_id))
        return JsonResponse(serializers.serialize('json', [text]), safe=False)
    except Exception as err:
        return JsonResponse({"error": f"get text given text id {text_id} fails: {str(err)}"})


def _download(request, func):
    """helper function for downloading"""
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as tmp:
            func(request, tmp)
            tmp.flush()
            return FileResponse(open(tmp.name, mode='rb'), as_attachment=True)

    except Exception as err:
        logger.error("Failed to download text" \
                     f"error message: {str(err)}")


@ensure_csrf_cookie
@require_http_methods(["POST"])
def download_texts(request):
    """download texts"""
    return _download(request, download_text_wrapper)


@ensure_csrf_cookie
@require_http_methods(["POST"])
def download_stats(request):
    """download statistics"""
    return _download(request, download_stats_wrapper)
