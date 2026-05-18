"""Module of tokenization
"""
import os
import subprocess

from pathlib import Path

from swegram_main.config import EFSELAB, UDPIPE, UDPIPE_MODEL
from swegram_main.lib.utils import write, AnnotationError


def tokenize(tokenizer: str, filepath: Path) -> None:
    try:
        if tokenizer.lower() == "efselab":
            subprocess.run(f"python3 {EFSELAB} --tokenized -o {filepath.parent} {filepath}".split(), check=True)
            
        elif tokenizer.lower() == "udpipe":
            response = subprocess.run(
                f"{str(UDPIPE)} --tokenize {str(UDPIPE_MODEL)} {filepath}".split(),
                capture_output=True, check=False
            )
            if response.returncode != 0:
                raise AnnotationError(f"Failed to tokenize: {response.stderr}")
            write(
                filepath=filepath.parent.joinpath(os.path.extsep.join([filepath.stem, "tok"])),
                context=response.stdout.decode()
            )

    except Exception as err:
        raise AnnotationError(f"Failed to tokenize, {err}") from err
