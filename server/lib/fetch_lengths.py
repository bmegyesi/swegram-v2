"""Fetch frequencies"""
from typing import Any, Dict

from sqlalchemy.orm import Session

from server.lib.utils import get_texts, get_type_and_pos_dicts
from swegram_main.config import PT_TAGS, SUC_TAGS


PUNCT_TAGS = [*SUC_TAGS[-3:], *PT_TAGS[-10:], "PUNCT"] 


def fetch_lengths(category: str, tagset: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    language = data["lang"]
    texts = get_texts(db, language, category=category)
    type_dict, pos_dict = get_type_and_pos_dicts(category=category, tagset=tagset, texts=texts)

    sorted_pos_list = [pos for pos, _ in sorted(pos_dict.items(), key=lambda x:x[1], reverse=True)]
    length_dict = {}  # {1: {PP: {word: count}}}

    for type_pos, count in type_dict.items():
        _type, pos = type_pos.rsplit("_", maxsplit=1)
        if pos in PUNCT_TAGS:
            continue
        length = len(_type)
        if length in length_dict:
            if pos in length_dict[length]:
                if _type in length_dict[length][pos]:
                    length_dict[length][pos][_type] += count
                else:
                    length_dict[length][pos][_type] = count
            else:
                length_dict[length][pos] = {_type: count}
        else:
            length_dict[length] = {pos: {_type: count}}

    length_list = [{
        "Length": {
            "total": length,
            "data": [
                {"type": pos, "count": sum(length_dict[length][pos].values())} for pos in length_dict[length].keys()
            ]
        },
        **{
            pos: {
                "total": sum(length_dict[length].get(pos, {}).values()),
                "data": [{"type": k, "count": v} for k, v in length_dict[length].get(pos, {}).items()]
            } for pos in sorted_pos_list
        }
    } for length in sorted(length_dict.keys())]

    data = {
        "number_of_texts": len(texts),
        "pos_list": [
            {
                "label": e, "prop": e
            } for e in ["Length", *sorted_pos_list, "Total"]
        ],
        "length_list": [{
            **length,
            "Total": {
                "total": sum([data_dict["count"] for data_dict in length["Length"]["data"]]),
                "data": []
            }
        } for length in length_list]
    }
    return data
