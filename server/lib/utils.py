"""utils"""
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Union
from swegram_main.data.features import Feature

def get_size_and_format(size_bytes: int) -> str:
    # Define the units and their respective sizes
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = size_bytes
    unit = 0

    # Iterate through units and convert size until it's less than 1024
    while size >= 1024 and unit < len(units) - 1:
        size /= 1024.0
        unit += 1

    # Format the size with two decimal places
    formatted_size = f"{size:.2f} {units[unit]}"
    return formatted_size


def convert_attribute_name(name: str) -> str:
    return {
        "text_id": "uuid",
        "filesize": "_filesize",
        "token_index": "index"
    }.get(name, name)


def convert_attribute_value(value: Any) -> Union[int, bool, str, Any]:
    if isinstance(value, (int, bool, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, OrderedDict):
        for k, v in value.items():
            if isinstance(v, Feature):
                value[k] = v.json
    return value
