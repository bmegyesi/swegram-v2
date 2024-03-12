import csv
import tempfile
from datetime import datetime
from typing import Any, Callable, Dict, List, IO, Optional, Tuple, Union

from fastapi.responses import FileResponse
import pandas as pd
from sqlalchemy.orm import Session

from server.lib.fetch_features import get_features_for_items
from server.lib.utils import get_texts
from server.models import Text, Paragraph, Sentence
from swegram_main.config import COLUMN_DELIMITER
from swegram_main.config import METADATA_DELIMITER_LEBAL as LEBAL
from swegram_main.config import METADATA_DELIMITER_TAG as TAG


S = Union[int, float]


class DownloadError(Exception):
    """Download Error"""



async def download_texts(data: Dict[str, Any], db: Session) -> FileResponse:
    language = data["lang"]
    download_format = data["outputForm"]
    texts = get_texts(db=db, language=language)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
        tmp_name = tmp.name
        Writer(file=tmp, texts=texts, language=language, download_format=download_format).download_texts()
        tmp.flush()

    return FileResponse(tmp_name, headers={"filename": tmp_name})


async def download_statistics(data: Dict[str, Any], db: Session) -> FileResponse:
    language = data["lang"]
    download_format = data["outputForm"]
    features = get_chosen_aspects_and_features(selected_indeces=data["chosenFeatures"], references=data["featureList"])
    texts = get_texts(db=db, language=language)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
        tmp_name = tmp.name
        Writer(
            file=tmp, texts=texts, language=language, download_format=download_format
        ).download_statistics(
            data["overviewOrDetail"], data["levels"], features
        )
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

    def download_texts(self) -> None:
        self._write_file_header()
        for index, text in enumerate(self.texts):
            self._write_text_header(text, index)
            self._write_text_body(text)

    def download_statistics(
        self, blocks: List[str], levels: List[str], features: Dict[str, Any]
    ) -> None:
        self.blocks = blocks
        self.levels = [self._c(level) for level in levels]
        self.features = features

        self._write_file_header(is_statistic_file=True)

        if self.format != ".xlsx":
            self.write(self._get_feature_string("Level/Aspect/Feature Name", "Scalar", "Mean", "Median"))
        else:
            self.column_indeces = ["Level/Aspect/Feature Name", "Scalar", "Mean", "Median"]
        if "overview" in blocks:
            self.download_statistics_block_all()
        if "detail" in blocks:
            self.download_statistics_block_ones()

        if self.format == ".xlsx":
            self.writer.close()

    def download_statistics_block_all(self):
        if self.format != ".xlsx":
            self.write(self._txt_format("Overview"))
            for level in self.levels:
                self.write(self._txt_format(f"Linguistic level: {level}"))
                aspects = get_features_for_items(level, self.texts, features=self.features)
                for aspect in aspects:
                    self.download_statistics_aspect_body(aspect)
        else:
            for level in self.levels:
                aspects = get_features_for_items(level, self.texts, features=self.features)
                for aspect in aspects:
                    self.download_statistics_aspect_body(aspect, sheet_name=f"overview-{level}-{aspect['aspect']}")

    def download_statistics_block_ones(self):
        self.aspects = [aspect for aspect in self.features]
        if self.format != ".xlsx":
            self.write(self._txt_format("Detail"))
            self.write("")
            for text in self.texts:
                if "text" in self.levels:
                    self.write(self._txt_format("Linguistic level: text"))
                    self.write(str(text))
                    for aspect in self.aspects:
                        self._download_features_for_aspect(text, aspect)
                    self.write("")
                if "paragraph" in self.levels:
                    self.write(self._txt_format("Linguistic level: paragraph"))
                    for paragraph in text.paragraphs:
                        self.write(str(paragraph))
                        for aspect in self.aspects:
                            self._download_features_for_aspect(paragraph, aspect)
                    self.write("")
                if "sentence" in self.levels:
                    self.write(self._txt_format("Linguistic level: sentence"))
                    for sentence in [s for p in text.paragraphs for s in p.sentences]:
                        self.write(str(sentence))
                        for aspect in self.aspects:
                            self._download_features_for_aspect(sentence, aspect)
                    self.write("")
                self.write("")
        else:
            for text in self.texts:
                if "text" in self.levels:
                    for aspect in self.aspects:
                        arrays = self._download_features_for_aspect(text, aspect)
                        self.write(
                            arrays=arrays, columns=self.column_indeces, sheet_name=f"detail-text-{aspect}"
                        )
                if "paragraph" in self.levels:
                    for i, paragraph in enumerate(text.paragraphs):
                        for aspect in self.aspects:
                            arrays = self._download_features_for_aspect(paragraph, aspect)
                            self.write(
                                arrays=arrays,
                                columns=self.column_indeces,
                                sheet_name=f"detail-paragraph-{i}-{aspect}"
                            )
                if "sentence" in self.levels:
                    for i, sentence in enumerate([s for p in text.paragraphs for s in p.sentences]):
                        for aspect in self.aspects:
                            arrays = self._download_features_for_aspect(sentence, aspect)
                            self.write(
                                arrays=arrays,
                                columns=self.column_indeces,
                                sheet_name=f"detail-sentence-{i}-{aspect}"
                            )

    def download_statistics_aspect_body(self, aspect: Dict[str, Any], sheet_name: Optional[str] = None):
        if self.format != ".xlsx":
            self.write(self._txt_format(f"Aspect: {aspect['aspect']}"))
            for feature_item in aspect["data"]:
                self._write_feature(feature_item)
        else:
            data = [self._write_feature(feature_item) for feature_item in aspect["data"]]
            self.write(arrays=data, columns=self.column_indeces, sheet_name=sheet_name)

    def _download_features_for_aspect(
        self, item: Union[Text, Paragraph, Sentence], aspect: str
    ) -> Optional[List[Tuple[str, S, S, S]]]:
        data = getattr(item, aspect)
        if self.format != ".xlsx":
            self.write(self._txt_format(f"Aspect: {aspect}"))
            for feature_name, feature_item in data.items():
                feature_item.update({"name": feature_name})
                self._write_feature(feature_item)
        else:
            return [
                self._write_feature({"name": feature_name, **feature_item})
                for feature_name, feature_item in data.items()
            ]

    def _get_feature_string(
        self, name: str, scalar: Union[int, float], mean: Union[int, float], median: Union[int, float]
    ) -> str:
        return f"{' ':>2}{name:>40}{'|':>4}{scalar:>10}{'|':>4}{mean:>10}{'|':>4}{median:>10}{'|':>4}"

    def _txt_format(self, string: str) -> str:
        return f"{string:^88}".replace(" ", "-")

    def _write_feature(self, feature_item: Dict[str, Any]) -> Optional[Tuple[str, S, S, S]]:
        name, scalar, mean, median = [feature_item.get(attr, "") for attr in ["name", "scalar", "mean", "median"]]
        if self.format == ".xlsx":
            return name, scalar, mean, median
        self.write(self._get_feature_string(name, scalar, mean, median))

    def _write_file_header(self, is_statistic_file: bool = False) -> None:
        file_headers = ["# Swegram", f"# Time: {_get_now()}", f"# Language: {self.language}"]

        if is_statistic_file:
            file_headers = [header_line.lstrip("# ") for header_line in file_headers ]
            file_headers.extend([
                " AND ".join(self.blocks),
                f"Texts: {', '.join([t.filename for t in self.texts])}",
                f"Linguistic levels: {', '.join(self.levels)}",
                f"Features: {', '.join(self.features)}"
            ])

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
        self.write(
            arrays=[token.conll(self.language, to_string=False) for p in text.paragraphs for s in p.sentences for token in s.tokens],
            columns=text.header(), sheet_name=text.filename
        )
        self.writer.close()

    def _raise_format_error(self):
        raise DownloadError(f"Unknown format to download: {self.format}")

    def _c(self, level: str) -> str:
        return {"para": "paragraph", "sent": "sentence"}.get(level, level)        


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
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _get_labels(text: Text) -> str:
    labels = text.labels if text.labels else {}
    return LEBAL.join([f"{k}{TAG}{v}" for k, v in labels.items()])


def _value2label(features: List[Any], v2l: Dict[int, str]) -> None:

    for feature_item in features:
        if "children" in feature_item:
            _value2label(feature_item["children"], v2l)
        v2l[feature_item["value"]] = feature_item["label"]


def get_chosen_aspects_and_features(
    selected_indeces: List[List[int]], references: List[Dict[str, Any]]
) -> Dict[str, Any]:

    features, v2l = {}, {}
    _value2label(references, v2l)
    for index_item in selected_indeces:
        _aspect_index, *_feature_index = index_item
        _aspect = v2l[_aspect_index]
        _feature = "_".join([v2l[fi] for fi in _feature_index])
        if _aspect in features:
            features[_aspect].append(_feature)
        else:
            features[_aspect] = [_feature]
    return features
