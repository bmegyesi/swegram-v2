
import argparse
from argparse import ArgumentParser
from pathlib import Path

"""
swegram 

positional arguments:
-l --language, denote which language
-i --input-path, denote input-file path


optional arguments:
-o --output-path, denote output-file path
-s --statistics, if statistics are required
-f --features [list]
--format str output, available [xlsx, json, txt]
--tokenize  bool
--tag       bool
--parse     bool
"""


DESCRIPTION = """
Swegram command line interface description
"""


def _annotation_parser(annotation_parser: ArgumentParser):
    """Add arguments for annotation parser"""
    annotation_parser.add_argument("--normalize", dest="NORMALIZE", action="store_true")
    annotation_parser.add_argument("--tokenize", dest="TOKENIZE", action="store_true")    
    annotation_parser.add_argument("--tag", dest="TAG", action="store_true")
    annotation_parser.add_argument("--parse", dest="PARSE", action="store_true")


def _statistic_parser(statistic_parser: ArgumentParser):
    """Add arguments for statistic parser"""
    statistic_parser.add_argument("--feature", dest="FEATURES", nargs="+", type=str)


def main_parser():
    """main parser for swegram command line interface"""
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog="SWGRAM 1.0")

    # positional arguments
    parser.add_argument("-l", "--language", type=str, choices=["en", "sv"], required=True,
                        help="choose the language for annotation")
    parser.add_argument("-i", "--input-path", type=Path, required=True,
                        help="The input path to files/directory where working files are stored")
    parser.add_argument("-o", "--output-dir", type=Path,
                        help="The output directory where working files are stored")
    parser.add_argument("--output-format", type=str, choices=["txt", "xlsx", "json", "csv"], default="txt",
                        help="The output format")

    subparsers = parser.add_subparsers(dest="command", help="Swegram subparser")

    annotation_parser = subparsers.add_parser("annotate", help="Annotation parser help")
    statistic_parser = subparsers.add_parser("statistic", help="Statistic parser help")

    _annotation_parser(annotation_parser)
    _statistic_parser(statistic_parser)

    args = parser.parse_args()
    return args
