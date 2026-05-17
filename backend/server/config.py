"""Configuration for server"""
import os
import shutil
from pathlib import Path
from shutil import SameFileError
from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field, field_validator, model_validator


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_DAYS = 7  # Days texts will be saved in the system
DEFAULT_ENGLISH_NORMALIZER = "histnorm_en"
DEFAULT_ENGLISH_PARSER = "udpipe"
DEFAULT_SWEDISH_NORMALIZER = "histnorm_sv"
DEFAULT_SWEDISH_PARSER = "efselab"
DEFAULT_OUTPUT_DIR = "output"


class Config(BaseModel):
    language: str
    input_path: Path
    filename: str
    model_config = ConfigDict(validate_default=True)
    output_dir: Optional[Path] = None

    checkNormalization: bool = False
    checkTokenize: bool = False
    checkPOS: bool = False

    @computed_field
    @property
    def tokenize(self) -> bool:
        return self.checkTokenize

    @computed_field
    @property
    def normalize(self) -> bool:
        return self.checkNormalization

    @computed_field
    @property
    def tag(self) -> bool:
        return self.checkPOS

    @computed_field
    @property
    def parse(self) -> bool:
        return self.checkPOS

    @computed_field
    @property
    def parser(self) -> str:
        if self.language == "sv":
            return DEFAULT_SWEDISH_PARSER
        if self.language == "en":
            return DEFAULT_ENGLISH_PARSER
        raise ValueError(f"Unsupported language: {self.language}")

    @computed_field
    @property
    def normalizer(self) -> str:
        if self.language == "sv":
            return DEFAULT_SWEDISH_NORMALIZER
        if self.language == "en":
            return DEFAULT_ENGLISH_NORMALIZER
        raise ValueError(f"Unsupported language: {self.language}")

    @field_validator("input_path")
    def validate_input_path(cls, value: Path) -> Path:
        if not value.exists():
            raise FileNotFoundError(value)
        return value

    @model_validator(mode="after")
    def set_config_for_output_dir(self) -> "Config":
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = self.input_path.absolute().parent.joinpath(DEFAULT_OUTPUT_DIR)
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir)
        try:
            shutil.copy(self.input_path, self.output_dir)
        except SameFileError:
            pass
        return self
