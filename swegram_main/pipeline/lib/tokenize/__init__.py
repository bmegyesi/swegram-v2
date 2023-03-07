"""Module of tokenization
"""
import os
import subprocess

from pathlib import Path

from swegram_main.lib.utils import write, AnnotationError
from swegram_main.config import EFSELAB_DIR, UDPIPE, UDPIPE_MODEL

def tokenize(tokenizer: str, filepath: Path) -> None:
    try:
        if tokenizer.lower() == "efselab":
            subprocess.run(f"python3 {EFSELAB_DIR} --tokenized -o {filepath.parent} {filepath}".split())
            
        elif tokenizer.lower() == "udpipe":
            response = subprocess.run(
                f"{UDPIPE} --tokenize {UDPIPE_MODEL} {filepath}".split(),
                capture_output=True
            )
            if response.returncode != 0:
                raise Exception(response.stderr)
            write(
                filepath=filepath.parent.joinpath(os.path.extsep.join([filepath.stem, "tok"])),
                context=response.stdout.decode()
            )

    except Exception as err:
        raise AnnotationError(f"Failed to tokenize, {err}")
