"""module of metdata

"""
import logging
import re
from typing import Dict, List

from swegram_main.config import METADATA_INITIAL, METADATA_FINAL, METADATA_DELIMITER_LEBAL, METADATA_DELIMITER_TAG


METADATA_LINE_PATTERN = fr"{METADATA_INITIAL}.*{METADATA_FINAL}"


class MetadataError(Exception):
    """Metadata error"""


def parse_metadata(line: str) -> Dict[str, str]:
    metadata = re.match(METADATA_LINE_PATTERN, line.strip())
    if metadata:
        try:
            metadata_content = metadata.group()[len(METADATA_INITIAL):-len(METADATA_FINAL)]
            return parse_metadata_helper(metadata_content)
        except MetadataError as err:
            logging.warning(err)
    return None


def parse_metadata_helper(metadata: str) -> Dict[str, str]:
    """Parse metadata"""
    tags = metadata.split(METADATA_DELIMITER_LEBAL)
    labels: Dict[str, str] = {}
    for tag in tags:
        try:
            key, value = tag.split(METADATA_DELIMITER_TAG, maxsplit=1)
            if key.strip() in labels:
                raise MetadataError(f"Duplicate metadata tags in same line, {metadata}")
            else:
                labels[key.strip()] = value.strip()
        except ValueError:
            raise MetadataError(f"Invalid Metadata Format: {metadata}")
    return labels


def convert_labels_to_list(labels: Dict[str, str]) -> List[str]:
    """Convert the dict of labels into a list of labels for later control/check"""
    return [*labels.keys(), *[f"{key}:{value}" for key, value in labels.items()]]
