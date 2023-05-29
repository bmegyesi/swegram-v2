
"""
swegram 

positional arguments:
-l --language, denote which language
-i --input-path, denote input-file path


optional arguments:
-o --output-path, denote output-file path
-s --statistics, if statistics are required
--format str output, available [txt, json, xlsx]
--tokenize  bool
--tag       bool
--parse     bool

"""

import argparse
from argparse import ArgumentParser, Namespace
from pathlib import Path

from swegram_main.config import ASPECTS, UNITS

DESCRIPTION = """
Swegram command line interface description
"""


def _annotation_parser(annotation_parser: ArgumentParser) -> None:
    """Add arguments for annotation parser"""
    annotation_parser.add_argument(
        "--normalize", dest="NORMALIZE", action="store_true",
        help="Process spelling checker after tokenization and"
             " normalized tokens will be used for upcoming annotation actions."
    )
    annotation_parser.add_argument(
        "--tokenize", dest="TOKENIZE", action="store_true",
        help="Process sentence segmentation and tokenization."
    )
    annotation_parser.add_argument(
        "--tag", dest="TAG", action="store_true",
        help="Process part-of-speech tagging."
    )
    annotation_parser.add_argument(
        "--parse", dest="PARSE", action="store_true",
        help="Process syntactic dependency parsing."
    )
    annotation_parser.add_argument(
        "--aggregate", dest="AGGREGATE", action="store_true",
        help="Aggregate all annotated texts into one file."
    )


def _statistic_parser(statistic_parser: ArgumentParser) -> None:
    """Add arguments for statistic parser"""
    statistic_parser.add_argument(
        "--include-metadata", dest="include_metadata",
        metavar="N", nargs="+", type=str, default=None,
        help="""Include certain texts by selecting metadata.
        For instance, --include-metadata key1 key2:value2, only selects the texts that contain
        key1 or key2:value2 in the metadata.
        """
    )
    statistic_parser.add_argument(
        "--exclude-metadata", dest="exclude_metadata",
        metavar="N", nargs="+", type=str, default=None,
        help="Exclude certain texts by deselecting metadata."
    )
    statistic_parser.add_argument(
        "-u", "--units", dest="UNITS", metavar="N", nargs="+",
        choices=UNITS, type=str, default=["corpus"],
        help="Checking statistics of features given certain linguistic unit(s)."
    )
    statistic_parser.add_argument(
        "--aspects", dest="ASPECTS", metavar="N", nargs="+",
        choices=ASPECTS, type=str, default=ASPECTS,
        help="Checking statistics based on the selection of certain aspect(s)."
    )
    statistic_parser.add_argument(
        "--include-features", dest="include_features", metavar="N", nargs="+",
        type=str, default=[],
        help="Only certain features will be included."
    )
    statistic_parser.add_argument(
        "--exclude-features", dest="exclude_features", metavar="N", nargs="+",
        type=str, default=[],
        help="Certain features will be excluded."
    )
    statistic_parser.add_argument("--print", dest="PPRINT", action="store_true", help="Print statistic on console")


def main_parser() -> Namespace:
    """main parser for swegram command line interface"""
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog="SWGRAM 1.0")

    # positional arguments
    parser.add_argument("-l", "--language", type=str, choices=["en", "sv"], required=True,
                        help="choose the language for annotation")
    parser.add_argument("-i", "--input-path", type=Path, required=True,
                        help="The input path to files/directory where working files are stored")
    parser.add_argument("-o", "--output-dir", type=Path,
                        help="The output directory where working files are stored")
    parser.add_argument("--save-as", type=str, choices=["txt", "xlsx", "json"], default="txt",
                        help="The output format")

    subparsers = parser.add_subparsers(dest="command", help="Swegram subparser")

    # optional arguments
    annotation_parser = subparsers.add_parser("annotate", help="Text annotation")
    statistic_parser = subparsers.add_parser("statistic", help="Statistic based on annotation")

    _annotation_parser(annotation_parser)
    _statistic_parser(statistic_parser)

    args = parser.parse_args()
    return args
