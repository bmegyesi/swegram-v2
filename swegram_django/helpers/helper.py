"""
the module of helper.py to create api
"""
import json
import logging

from django.core import serializers
from django.db.models import Q
from swegram_main.models import TextStatsModel
from swegram_main.api.helpers.download_utils import download_helper, download_stats_helper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


QUERY_DELIMITER = "&"
ATTRIBUTOR_DELIMITER = "="
_INTEGER_ATTRIBUTES = ['pk', 'text_id', 'number_of_paragraphs', 'number_of_sentences']
_BOOLEAN_ATTRIBUTES = ['activated', 'normalized', 'parsed', 'has_label']


class QueryFormatError(Exception):
    """Query format error"""


def _convert(key, value):
    """convert value data type according to the key"""
    if key in _INTEGER_ATTRIBUTES:
        return int(value)
    if key in _BOOLEAN_ATTRIBUTES:
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise QueryFormatError(f"Expected true or false but got {value} instead")
    return value


def _query_parser(query: str) -> dict:
    """to parse the query into a dict"""
    return {
        key: _convert(key, value) for key, value in [ 
            q.split(ATTRIBUTOR_DELIMITER) for q in query.split(QUERY_DELIMITER)
        ]
    }


def search_text_helper(query: str) -> dict:
    """search texts given the query"""
    try:
        parsed_query = _query_parser(query)
    except Exception as err:
        raise QueryFormatError(
            f"Failed to parse the query, {str(err)}"
        )
    else:
        return json.loads(
            serializers.serialize(
              'json',
              TextStatsModel.objects.all().filter(**parsed_query)
            )
        )


def get_text_helper() -> dict:
    """get the current text states"""
    return json.loads(
        serializers.serialize(
            'json', TextStatsModel.objects.all()
        )
    )


def _fetch_selected_text_ids(texts) -> list:
    """fetch the selected text ids from texts"""
    return [t.text_id for t in texts if t.activated]


def _update_metadata(metadata, texts) -> list:
    """update metadata"""
    options = []
    value = 1
    text_ids = [t.text_id for t in texts]
    texts_with_metadata = set()
    if metadata:
        for label, value_dict in metadata.items():
            has_values = [False] * len(value_dict.keys())
            for index, key in enumerate(value_dict.keys()):
                for i, (text_id, _) in enumerate(value_dict[key]):
                    if text_id in text_ids:
                        has_values[index] = True
                        texts_with_metadata.add(text_id)
                    else:
                        del value_dict[key][i]
            values = [
              {
                  'label':key,
                  'value': value + index,
                  'children':[
                      {
                        'value': v, 
                        'label': l
                      } for v,l in value_dict[key]
                  ]
              } for index, key in enumerate(value_dict.keys(), 1) if has_values[index-1]]
            if values:
                options.append({'value':value, 'label':label, 'children': values})
                value += len(value_dict) + 1
    
    return {
        "options": options, 
        "texts_with_metadata": list(texts_with_metadata)
    }


def _fetch_text_ids_and_filenames(texts) -> list:
    """fetch text ids"""
    return [(t.text_id, t.filename) for t in texts]


def _remove_non_existing_texts(texts) -> list:
    """remove the texts that does not exist in the database"""
    return [TextStatsModel.objects.get(pk=t.get('pk')) for t in texts if TextStatsModel.objects.filter(pk=t.get('pk'))]


def _fetch_data(metadata, texts) -> dict:
    """reset data for frontend"""
    return {
      'text_ids': _fetch_text_ids_and_filenames(texts),       # work with text selection 
      'selected_text_ids': _fetch_selected_text_ids(texts),   # work with text selection 
      'name':'label',            # work with metadata
      **_update_metadata(metadata, texts)
    }


def _load_request_body(request) -> dict:
    """load request body"""
    return json.loads(request.body)


def update_text_helper(request):
    """generate the data used for frontend"""
    body = _load_request_body(request)
    texts = _remove_non_existing_texts(body.get('texts', []))
    metadata = body.get('metadata', [])
    return _fetch_data(metadata=metadata, texts=texts)


def download_stats_wrapper(request, temp_file):
    """download text to the local"""
    try:
        text_list = get_text_list(request)
        body = json.loads(request.body)
        lang = body.get('lang')
        output_format = body.get('outputForm')
        overview_detail = body.get('overviewOrDetail')
        levels = body.get('levels')
        selected_features = body.get('chosenFeatures')
        feature_list = body.get('featureList')
        download_stats_helper(
            text_list, lang, output_format, temp_file,
            overview_detail, levels, selected_features, feature_list
        )
    except Exception as err:
        logger.error("Failed to download annotated texts: "
                     f"error message: {str(err)}")


def download_text_wrapper(request, temp_file):
    """download statistics to the local"""
    try:
        body = json.loads(request.body)
        lang = body.get('lang')
        output_format = body.get('outputForm')
        text_list = get_text_list(request)
        download_helper(text_list, lang, output_format, temp_file)
    except Exception as err:
        logger.error("Failed to download statistics: "
                     f"error message: {str(err)}")


def get_text_list(request, category=''):
    """get text list given request"""
    try:
        body = json.loads(request.body)
        
        text_list = []
        for text in body.get('texts', dict()).get(body.get('lang'), []):
            try:
                text_object = TextStatsModel.objects.get(pk=text.get("pk"))
                if text_object.activated:
                    text_list.append(text_object)
            except Exception as err:
                logger.error("Failed to fetch text metadata from database\n"
                             f"search query -> lang: {body.get('lang')}, pk: {text.get('pk')}\n"
                             f"erorr message: {str(err)}")
        
        if category.startswith("norm"):
            text_list = [text for text in text_list if text.normalized]
        elif category in ["parsed", "lemma"]:
            text_list = [text for text in text_list if text.parsed]

        return text_list
    except Exception as err:
        logger.error("Failed to get text list from database"
                     f"error message: {str(err)}")


    