
import os
from setuptools import setup
from typing import List


def read(fname: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), fname)) as input_file:
        return input_file.read()


def get_requirements(requirement: str) -> List[str]:
    return [dependency.strip() for dependency in read(requirement).split("\n") if dependency.strip()]


setup(
    name="Swegram CLI",
    version="1.0.0",
    # author="",
    # author_email="",
    description="Swegram description",
    long_description=read("README.md"),
    # packages=[],
    license=read("LICENSE"),
    # url="url",
    # requires=get_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "swegram=swegram_main.handler.cli:main"
        ]
    }
)
