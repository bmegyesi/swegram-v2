"""Fetch frequencies"""
from typing import Any, Dict

from sqlalchemy.orm import Session

from server.lib.utils import get_texts, get_type_and_pos_dicts


def fetch_frequencies(category: str, tagset: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    language = data["lang"]
    texts = get_texts(db, language, category=category)
    type_dict, pos_dict = get_type_and_pos_dicts(category=category, tagset=tagset, texts=texts)

    return {
        f"{category}_pos": [
            {
                "count": c, "pos": k.split("_", maxsplit=1)[-1], category: k.rsplit("_", maxsplit=1)[0]
            } for k, c in sorted(list(type_dict.items()), key=lambda x:x[1], reverse=True)
        ],
        "pos_list": sorted(pos_dict.items(), key=lambda x:x[1], reverse=True),
        "number_of_texts": len(texts)
    }
