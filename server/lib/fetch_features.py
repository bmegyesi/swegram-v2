"""post data"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.models import Text
from server.lib.utils import get_texts
from swegram_main.config import SUC_TAGS, PT_TAGS, PAGE_SIZE
from swegram_main.lib.utils import mean, median


ASPECT_LIST = ["general", "readability", "morph", "lexical", "syntactic"]


class Annotation(BaseModel):
    """annotation type"""
    valid_texts: List[Any] = []
    invalid_texts: List[Any] = []

    @property
    def number_of_valid_texts(self) -> int:
        return len(self.valid_texts)

    def append_text(self, text: Text, valid: bool = False):
        if valid:
            self.valid_texts.append([text.id, text.filename])
        else:
            self.invalid_texts.append([text.id, text.filename])


class State(BaseModel):
    normalized: Optional[Annotation] = None
    parsed: Optional[Annotation] = None
    tokenized: Optional[Annotation] = None
    total_para_items: int = 0
    total_sent_items: int = 0
    total_text_items: int = 0


def post_states(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """post states"""
    language = data["lang"]
    texts = get_texts(db, language) 
    normalized, parsed, tokenized = [Annotation() for _ in range(3)]
    _texts, paragraphs, sentences = 0, 0, 0
    for text in texts:
        normalized.append_text(text, text.normalized)
        parsed.append_text(text, text.parsed)
        tokenized.append_text(text, text.tokenized)
        if text.parsed:
            paragraphs += len(text.paragraphs)
            sentences += text.sents
            _texts += 1

    return State(
        normalized=normalized,
        parsed=parsed,
        tokenized=tokenized,
        total_para_items=paragraphs,
        total_sent_items=sentences,
        total_text_items=_texts
    ).model_dump()


def get_features(element: str, index: int, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    size = PAGE_SIZE
    language = data["lang"]
    texts = get_texts(db, language)
    start_index = (index - 1) * size
    statistics_data, content = [], []
    if texts:
        if element == "text":
            content = texts[start_index:start_index + size]
        elif element in ["sent", "para"]:
            content = []
            for text in texts:
                number = text.sents if element == "sent" else len(text.paragraphs)
                if number <= start_index:
                    start_index -= number
                    continue
                items = [s for p in text.paragraphs for s in p.sentences] if element == "sent" else text.paragraphs
                content.extend(items[start_index:start_index + size])
                if len(content) < size:
                    start_index = 0
                    size -= len(items[start_index:start_index + size])
                else:
                    break
        else:
            return {"error": f"Invalid element level {element=}"}

        for i, _content in enumerate(content, start_index):
            statistics_data.append({
                "id": i, "data": [
                    {
                        "aspect": aspect,
                        **{"data": [
                            {
                                "name": k, **v
                            } for k, v in _content.as_dict()[aspect].items()]}
                    } for aspect in ASPECT_LIST if _content.as_dict().get(aspect)
                ]
            })

    return {
        "content": [str(i) for i in content],
        "statistics": statistics_data,
        "number_of_texts": len(texts)
    }


def get_features_for_elements(elements: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    language = data["lang"]
    texts = [t for t in get_texts(db, language)]
    if elements == "texts":
        contents = texts
    elif elements == "paras":
        contents = [p for t in texts for p in t.paragraphs]
    elif elements == "sents":
        contents = [s for t in texts for p in t.paragraphs for s in p.sentences]
    else:
        raise

    aspect_data = []
    for aspect in ASPECT_LIST:
        _aspect_dict = {}
        _aspect_content_list = [content.as_dict()[aspect] for content in contents]
        for _aspect_content in _aspect_content_list:
            for feature_name, feature_data in _aspect_content.items():
                if feature_name in _aspect_dict:
                    for metric in ["mean", "median", "scalar"]:
                        _aspect_dict[feature_name][metric].append(feature_data.get(metric))
                else:
                    _aspect_dict[feature_name] = {
                        "mean": [feature_data.get("mean")],
                        "median": [feature_data.get("median")],
                        "scalar": [feature_data.get("scalar")]
                    }
        for feature_name, feature_data in _aspect_dict.items():
            
            _aspect_dict[feature_name]["mean"] = mean([value for value in feature_data["mean"] if value != ""])
            _aspect_dict[feature_name]["median"] = median([value for value in feature_data["median"] if value != ""])
            _aspect_dict[feature_name]["scalar"] = sum([value for value in feature_data["scalar"] if value])


        aspect_data.append({
            "aspect": aspect,
            **{"data": [{"name": k, **v} for k, v in _aspect_dict.items()]}
        })

    return {"data": aspect_data}