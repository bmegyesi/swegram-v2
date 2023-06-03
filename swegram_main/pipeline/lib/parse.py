"""Module of parsing


When it commes to efselab, there is no standalone command to run parsing.
The parse action is built on top of tagging. Here we assume that the user
has file.tag and want to parse alone. We break up the code and provide a
workaround solution for parsing according to efselab coding

Attention: export pythonpath for efselab directory
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


from swegram_main.pipeline.lib.tag import write_tagged_conll, TaggingError
from swegram_main.lib.utils import write, AnnotationError
from swegram_main.config import EFSELAB_DIR, UDPIPE, UDPIPE_MODEL


EFSELAB_MODEL = os.path.join(EFSELAB_DIR, "swe-pipeline")
MALT = os.path.join(EFSELAB_MODEL, "maltparser-1.9.0/maltparser-1.9.0.jar")
PARSING_MODEL = os.path.join(EFSELAB_MODEL, "old-swe-ud")


class ParsingError(Exception):
    """Error for standalone parse action"""


def parse_from_tagged_file(filepath: Path) -> None:
    """parse swedish text given a .tag file
    """
    if filepath.suffix != ".tag":
        raise ParsingError(f"Expected to get .tag, but got {filepath.suffix}.")

    with tempfile.TemporaryDirectory() as tagged_conll_dir:
        try:
            write_tagged_conll(filepath)
        except TaggingError:
            print("Try with original tag file.")
        shutil.copy(PARSING_MODEL + ".mco", tagged_conll_dir)
        parsed_filename = os.path.join(tagged_conll_dir, f"{filepath.stem}{os.path.extsep}conll")
        parser_cmdline = [
            "java",
            "-Xmx2000m",
            "-jar", MALT,
            "-m", "parse",
            "-i", filepath.absolute().as_posix(),
            "-o", parsed_filename,
            "-w", tagged_conll_dir,
            "-c", os.path.basename(PARSING_MODEL)
        ]
        subprocess.run(parser_cmdline, check=False)
        shutil.copy(parsed_filename, filepath.parent)


def parse(parser: str, filepath: Path) -> None:
    try:
        if parser.lower() == "efselab":
            parse_from_tagged_file(filepath)

        elif parser.lower() == "udpipe":
            response = subprocess.run(
                f"{UDPIPE} --parse --input=conllu {UDPIPE_MODEL} {filepath}".split(),
                capture_output=True, check=False
            )
            if response.returncode != 0:
                raise AnnotationError(response.stderr.decode())
            write(
                filepath=filepath.parent.joinpath(os.path.extsep.join([filepath.stem, "conll"])),
                context=response.stdout.decode()
            )

    except Exception as err:
        raise AnnotationError(f"Failed to tokenize, {err}") from err
