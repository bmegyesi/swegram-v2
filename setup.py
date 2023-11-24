
from pathlib import Path
from setuptools import setup, find_packages
from typing import List
from swegram_main.version import VERSION

Base = Path(__file__).parent.resolve()


def get_requirements() -> List[str]:
    """Get Requirements"""
    with (Path(__file__).parent / "requirements.txt").open("r") as f:
        return f.read().splitlines()


setup(
    name="swegram",
    version=VERSION,
    description="CLI library for Swegram",
    long_description=(Base / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tools*", "test*", "swegram/*", "swegram_django*"]),
    license=(Base / "LICENSE.md").read_text(encoding="utf-8"),
    url="https://github.com/bmegyesi/swegram-v2",
    install_requires=get_requirements(),
    package_data={
        "swegram_main.statistics.kelly": ["kelly.en", "kelly.sv", "wpm.sv"],
        "build_dependencies": ["install.sh"],
        "build_dependencies.en.en": ["english-ud-2.0-170801.udpipe"],
        "build_dependencies.en.histnorm": ["bnc.mono.en.freqs"],
        "build_dependencies.en.histnorm.WordNetDictionary": [
            "adj.exc", "adv.exc", "data.adj", "data.adv", "data.noun", "data.verb", "noun.exc", "verb.exc"
        ],
        "build_dependencies.sv": ["swe-pipeline-ud2.tar.gz"],
        "build_dependencies.sv.HistNorm.scripts": [
            "compute_editdistance.perl",
            "extractWeights.perl",
            "findEdits.perl",
            "normalise_levenshtein.perl",
            "normalise_levenshtein_elevtexter.perl",
            "setWeightsAndThreshold.sh",
            "set_threshold.perl"
        ],
        "build_dependencies.sv.HistNorm.resources.swedish.levenshtein": [
            "fullList.txt",
            "saldo-total_wordforms.txt",
            "sv-threshold.txt",
            "sv-weights.txt",
            "swedish.corp",
            "swedish.dev.txt",
            "swedish.dic",
            "swedish.hs-sv.dev.hs",
            "swedish.hs-sv.dev.hssv",
            "swedish.hs-sv.dev.sv",
            "swedish.hs-sv.test.hs",
            "swedish.hs-sv.test.hssv",
            "swedish.hs-sv.test.sv",
            "swedish.hs-sv.train.hs",
            "swedish.hs-sv.train.hssv",
            "swedish.hs-sv.train.sv",
            "swedish.train.txt",
            "threshold.swedish.elevtexter.txt",
            "threshold.swedish.txt",
            "weights.swedish.txt"
        ]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "swegram=swegram_main.handler.cli:main",
            "swegram-build=swegram_main.handler.build:main"
        ]
    }
)
