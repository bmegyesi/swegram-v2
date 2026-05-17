"""Module of pipeline
"""
import logging
from pathlib import Path
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from server.config import Config
from server.database.handler import DatabaseHandler
from server.lib.decorators import JobDecorator, TaskDecorator
from server.models import Text as TextDataBaseModel
from swegram_main.data.texts import TextDirectory as TD
from swegram_main.data.texts import Text as TextData
from swegram_main.handler.handler import load_text
from swegram_main.lib.utils import get_size,read_conll_text
from swegram_main.lib.logger import get_logger
from swegram_main.pipeline.lib.normalize import normalize
from swegram_main.pipeline.lib.parse import parse
from swegram_main.pipeline.lib.tag import tag
from swegram_main.pipeline.lib.tokenize import tokenize
from swegram_main.pipeline.preprocess import preprocess
from swegram_main.pipeline.postprocess import postprocess as _postprocess


logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class PreProcessError(Exception):
    """Preprocess Error"""


@JobDecorator()
def preprocess_job(config: Config, **kwargs) -> Tuple[int, List[TD]]:
    """preprocess job to split the input file into texts"""
    logger.info(f"Starting preprocessing for {config.input_path} in {config.language}")
    if "raw_text" not in kwargs:
        raise PreProcessError(f"Not found raw text from input, {kwargs=}")
    save_text(target_path=config.input_path, **kwargs)
    try:
        if "job_id" not in kwargs:
            raise ValueError("job_id is not provided in kwargs for preprocess_job")
        return kwargs["job_id"], preprocess(config.input_path, config.output_dir, config.parser, **kwargs)
    except Exception as e:
        raise PreProcessError(f"Error occurred while preprocessing {config.input_path}: {e}") from e
    finally:
        config.output_dir.joinpath(config.input_path.name).unlink(missing_ok=True)


@TaskDecorator()
def save_text(raw_text: str, target_path: Path, **kwargs) -> None:
    with open(target_path, mode="w", encoding="utf-8") as f:
        f.write(raw_text)


@JobDecorator()
def annotate_text(text: TD, config: Config, parent_id: int, **kwargs) -> None:
    logger.info(f"Starting annotating for {config.input_path} in {config.language}")
    if config.normalize:
        tokenize_task(config.parser, text, **kwargs)
        normalize_task(config.normalizer, text, **kwargs)
    if config.tokenize and not config.normalize:
        tokenize_task(config.parser, text, **kwargs)
    if config.parse:
        if not text.tag.exists():
            tag_task(config.parser, text, **kwargs)
        parse_task(config.parser, text, **kwargs)

    postprocess_task(text, config.parser, "txt", **kwargs)
    load_text_task(text, config, **kwargs)


@TaskDecorator()
def postprocess_task(text: TD, parser: str, format: str = "txt", **kwargs) -> None:
    _postprocess(text=text, model=parser, save_as=format)


@TaskDecorator()
def load_text_task(text: TD, config: Config, **kwargs) -> None:
    paragraphs, labels = read_conll_text(input_path=text.conll)
    _text: TextData = load_text(
        text=paragraphs,
        labels=labels if labels else {},
        language=config.language,
        filename=config.filename,
        parsed=config.parse
    )
    try:
        db: Session = DatabaseHandler().SessionLocal()
        seralized_text_data = _text.to_dict()
        seralized_text_data.update({
            "tokenized": config.tokenize, "normalized": config.normalize, "tagged": config.tag,
            "parsed": config.parse, "filesize": config.filesize
        })
        text_instance = TextDataBaseModel(**seralized_text_data)
        db.add(text_instance)
        db.commit()
        db.refresh(text_instance)
        text_instance.load_data([p.to_dict() for p in _text.paragraphs], db)
    finally:
        db.close()


@TaskDecorator()
def normalize_task(normalizer: str, text: TD, **kwargs) -> None:
    if not text.spell.exists():
        normalize(normalizer, text.tok)
    else:
        logger.info(f"Skipping normalization for {text} as norm file already exists.")


@TaskDecorator()
def tag_task(parser: str, text: TD, **kwargs) -> None:
    if not text.tag.exists():
        if not text.spell.exists() and not text.tok.exists():
            raise FileNotFoundError("No tokenized file found")
        tag(parser, text.spell if text.spell.exists() else text.tok)
    else:
        logger.info(f"Skipping pos tagging for {text} as tag file already exists")


@TaskDecorator()
def parse_task(parser: str, text: TD, **kwargs) -> None:
    if not text.conll.exists():
        parse(parser, text.tag)
    else:
        logger.info(f"Skipping parsing for {text} as conll file already exists.")


@TaskDecorator()
def tokenize_task(parser: str, text: TD, **kwargs) -> None:
    if not text.tok.exists():
        tokenize(parser, text.filepath)
    else:
        logger.info(f"Skipping tokenization for {text} as tok file already exists.")


def annotate_file(language: str, filepath: Path, output_dir: Optional[Path] = None, **kwargs) -> None:
    """Annotate the input file"""
    config = Config(language=language, input_path=filepath, output_dir=output_dir, **kwargs)
    parent_id, texts = preprocess_job(config=config, job_name="Preprocess", **kwargs)
    base_filename, suffix = config.filename.split(".")
    for index, text in enumerate(texts, 1):
        if len(texts) > 1:
            config.filename = f"{base_filename}_{index}.{suffix}"
        config.filesize = get_size(text.filepath)
        annotate_text(text=text, config=config, parent_id=parent_id, job_name="Annotation")
