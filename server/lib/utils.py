"""utils.py"""
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from server.models import Text


def get_texts(db: Session, language: str, category: Optional[str] = None) -> List[Text]:

    texts = db.query(Text).filter( Text.language == language ).filter( Text.activated == True )

    if category == "norm":
        return [ text for text in texts.filter( Text.normalized == True )]
    if category == "lemma":
        return [ text for text in texts.filter( Text.tagged == True )]

    return [ text for text in texts]


def get_type_and_pos_dicts(category: str, tagset: str, texts: List[Text]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    type_dict, pos_dict = {}, {}
    for text in texts:
        for type_pos, count in text.as_dict()[f"freq_{category}_dict_{tagset}"].items():
            _, pos = type_pos.rsplit("_", maxsplit=1)
            if pos in pos_dict:
                pos_dict[pos] += count
            else:
                pos_dict[pos] = count
            if type_pos in type_dict:
                type_dict[type_pos] += count
            else:
                type_dict[type_pos] = count
    return type_dict, pos_dict
