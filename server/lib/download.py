import tempfile
from datetime import datetime
from typing import Any, Dict, List, IO, Optional

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from server.lib.utils import get_texts
from server.models import Text


async def download_texts(data: Dict[str, Any], db: Session) -> FileResponse:
    language = data["lang"]
    texts = get_texts(db=db, language=language)

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
        tmp_name = tmp.name
        generate_texts(texts, language, tmp)
        tmp.flush()

    return FileResponse(tmp_name, headers={"filename": tmp_name})


def generate_texts(texts: List[Text], language: str, file: IO[Any]) -> None:
    _generate_txt_file_header(language, file)
    for index, text in enumerate(texts):
        _generate_txt(text, index, file)


def _generate_txt_file_header(language: str, file: IO[Any]) -> str:
    """generate file header"""
    time_stamp = datetime.now().strftime("%Y-%m-%d %H%M")
    file_header = "\n".join(["# Swegram", f"# Time: {time_stamp}", f"# Language: {language}"])
    file.write(file_header)


def _generate_txt(text: Text, index: int, file: IO[Any]) -> None:
    _generate_txt_text_header(text, index, file)
    _generate_txt_text_body(text, file)


def _generate_txt_text_header(text: Text, index: Optional[int], file: IO[Any]) -> None:
    """generate text header"""

    header = "\n".join([
        f"\n\n# Name: {_get_original_filename(text.filename)}",
        f"# Size: {text.filesize}", "# Tokenized: True", f"# Normalized: {text.normalized}",
        f"# PoS tagged: {text.parsed}", f"# Created time: {text.date}\n\n"
    ])

    if index > 0 and not text.has_labels:
        header = "<>\n" + header.lstrip()

    file.write(header)


def _generate_txt_text_body(text: Text, file: IO[Any]) -> None:

    for paragraph in text.paragraphs:
        for sentence in paragraph.sentences:
            for token in sentence.tokens:
                file.write(token.conll(text.language))
                file.write("\n")
            file.write("\n")
        file.write("\n")


def _get_original_filename(filename: str) -> str:
    _stem, extension = filename.rsplit(".", maxsplit=1)
    stem, _ = _stem.rsplit("_", maxsplit=1)
    return f"{stem}.{extension}"
