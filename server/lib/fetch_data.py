"""Fetch data"""
from typing import Any, Dict, List, Tuple
from server.models import Text


def _fetch_text_ids_and_filenames(texts: List[Text]) -> List[Tuple[int, str]]:
    """Fetch text ids"""
    return [(t.id, t.filename) for t in texts]


def _fetch_selected_text_ids(texts: List[Text]) ->  List[int]:
    """Fetch the selected text ids from texts"""
    return [t.id for t in texts if t.activated]


def _update_metadata(metadata: Dict[str, Any], texts: List[Text]) -> Dict[str, Any]:
    options = []
    value = 1
    text_ids = [t.id for t in texts]
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


def fetch_data(metadata: Any, texts: List[Text]) -> Dict[str, Any]:
    """Reset data for frontend"""
    return {
        "text_ids": _fetch_text_ids_and_filenames(texts),
        "selected_text_ids": _fetch_selected_text_ids(texts),
        **_update_metadata(metadata["metadata"], texts)
    }
