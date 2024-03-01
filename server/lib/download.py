import csv
import tempfile
from datetime import datetime
from typing import Any, Callable, Dict, List, IO, Optional, Tuple

from fastapi.responses import FileResponse
import pandas as pd
from sqlalchemy.orm import Session

from server.lib.utils import get_texts
from server.models import Text
from swegram_main.config import COLUMN_DELIMITER
from swegram_main.config import METADATA_DELIMITER_LEBAL as LEBAL
from swegram_main.config import METADATA_DELIMITER_TAG as TAG


class DownloadError(Exception):
    """Download Error"""



async def download_texts(data: Dict[str, Any], db: Session) -> FileResponse:
    language = data["lang"]
    download_format = data["outputForm"]
    texts = get_texts(db=db, language=language)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
        tmp_name = tmp.name
        Writer(file=tmp, texts=texts, language=language, download_format=download_format).generate()
        tmp.flush()

    return FileResponse(tmp_name, headers={"filename": tmp_name})


class Writer:

    def __init__(self, file: IO[Any], texts: List[Text], language: str, download_format: str) -> None:
        self.file = file
        self.texts = texts
        self.language = language
        self.format = download_format
        self.writer = self._get_writer()
        self.write = self._write()

    def _get_writer(self) -> IO[Any]:
        if self.format == ".txt":
            return self.file
        if self.format == ".csv":
            return csv.writer(self.file, delimiter=COLUMN_DELIMITER, escapechar="\\", quoting=csv.QUOTE_NONE)
        if self.format == ".xlsx":
            return pd.ExcelWriter(path=self.file.name, engine="openpyxl")

        self._raise_format_error()

    def _write(self) -> Callable:
        if self.format == ".txt":
            return lambda string: self.writer.write(f"{string}\n")
        if self.format == ".csv":
            return lambda string: self.writer.writerow(string.split("\t") if string else [" "])
        if self.format == ".xlsx":
            return self._write2xlsx

        self._raise_format_error()

    def _write2xlsx(
        self, arrays: List[List[str]], sheet_name: str,
        indeces: Optional[List[str]] = None, columns: Optional[List[str]] = None 
    ) -> None:

        if columns:
            if indeces:
                df = pd.DataFrame(arrays, index=indeces, columns=columns)
                df.to_excel(self.writer, columns=columns, sheet_name=sheet_name)
            else:
                df = pd.DataFrame(arrays, columns=columns)
                df.to_excel(self.writer, index=False, columns=columns, sheet_name=sheet_name)
        else:
            if indeces:
                df = pd.DataFrame(arrays, index=indeces)
                df.to_excel(self.writer, header=False, sheet_name=sheet_name)
            else:
                df = pd.DataFrame(arrays)
                df.to_excel(self.writer, header=False, index=False, sheet_name=sheet_name)

    def generate(self):
        self._write_file_header()
        for index, text in enumerate(self.texts):
            self._write_text_header(text, index)
            self._write_text_body(text)

    def _raise_format_error(self):
        raise DownloadError(f"Unknown format to download: {self.format}")

    def _write_file_header(self):
        file_headers = ["# Swegram", f"# Time: {_get_now()}", f"# Language: {self.language}"]
        if self.format != ".xlsx":
            for header_line in file_headers:
                self.write(header_line)
            self.write("")
        else:
            index_list, data = _get_index_and_data(file_headers)
            self.write(arrays=data, indeces=index_list, sheet_name="Info for annotated file")

    def _write_text_header(self, text: Text, index: Optional[int]) -> None:
        """Write text header"""
        lines = [
            f"# Filename: {_get_original_filename(text.filename)}",
            f"# Size: {text.filesize}",
            "# Tokenized: True",
            f"# Normalized: {text.normalized}",
            f"# PoS Tagging & Parsing: {text.tagged}"
        ]
        label_line = _get_labels(text)

        if self.format != ".xlsx":
            if label_line or index:
                lines.append(label_line)
            for line in lines:
                self.write(line)
            self.write("")
        else:
            if label_line:
                lines.append(f"# Text Label: {label_line}")
            index_list, data = _get_index_and_data(lines)
            self.write(arrays=data, sheet_name="Info for annotated text", indeces=index_list)

    def _write_text_body(self, text: Text) -> None:
        """Write text body"""
        if self.format == ".xlsx":
            self._write_xlsx_text_body(text)
            return
        for paragraph in text.paragraphs:
            for sentence in paragraph.sentences:
                for token in sentence.tokens:
                    self.write(token.conll(self.language))
                self.write("")
            self.write("")

    def _write_xlsx_text_body(self, text: Text) -> None:
        arrays=[token.conll(self.language, to_string=False) for p in text.paragraphs for s in p.sentences for token in s.tokens]
        print(arrays)
        print(text.header())
        breakpoint()
        self.write(
            arrays=arrays,
            columns=text.header(), sheet_name=text.filename
        )
        self.writer.close()


def _get_index_and_data(lines: List[str]) -> Tuple[List[str], List[List[str]]]:
    index_list, values = [], []
    for line in lines:
        if ":" in line:
            index, value = line.split(":", maxsplit=1)
            index_list.append(index)
            values.append([value.strip()])
        else:
            index_list.append(line)
            values.append([""])
    return index_list, values


def _get_original_filename(filename: str) -> str:
    _stem, extension = filename.rsplit(".", maxsplit=1)
    stem, _ = _stem.rsplit("_", maxsplit=1)
    return f"{stem}.{extension}"


def _get_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H%M")


def _get_labels(text: Text) -> str:
    labels = text.labels if text.labels else {}
    return LEBAL.join([f"{k}{TAG}{v}" for k, v in labels.items()])
