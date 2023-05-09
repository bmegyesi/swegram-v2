
import os
from pathlib import Path
from setuptools import setup, find_packages
from typing import List


def read(fname: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), fname)) as input_file:
        return input_file.read()


def get_requirements() -> List[str]:
    """Get Requirements"""
    with (Path(__file__).parent / "requirements.txt").open("r") as f:
        return f.read().splitlines()


setup(
    name="swegram",
    version="1.0.0.dev0",
    # author="",
    # author_email="",
    description="CLI library for Swegram",
    # long_description=read("README.md"),
    packages=find_packages(exclude=["tools*", "test*"]),
    license=read("LICENSE"),
    # url="url",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "swegram=swegram_main.handler.cli:main"
        ]
    }
)
