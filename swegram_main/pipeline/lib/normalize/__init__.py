"""Module of normalization

Requirements for normalization

histnorm_en:
    1. Folder WordNetDictionary
    2. bnc.mono.en.freqs
    3. engGramp2.py

histnorm_sv:

"""
import os
import subprocess

from pathlib import Path
from swegram_main.lib.utils import write, AnnotationError
from swegram_main.config import EFSELAB_DIR, UDPIPE, UDPIPE_MODEL, HISTNORM_SV
from swegram_main.pipeline.lib.normalize.engGramp2 import enggram_spellcheck


RESOURCE = os.path.join(HISTNORM_SV, "resources", "swedish", "levenshtein")


def _convert_english_normalized_filepath(filepath: Path) -> None:
    ...


def normalize(normalizer: str, filepath: Path) -> None:
    try:
        output_file = filepath.parent.joinpath(os.path.extsep.join([filepath.stem, 'spell']))
        if normalizer.lower() == "histnorm_sv":
            response = subprocess.run(
                f"perl -CSAD {os.path.join(HISTNORM_SV, 'scripts', 'normalise_levenshtein_elevtexter.perl')} " \
                f"{filepath} {os.path.join(RESOURCE, 'swedish.dic')} " \
                f"{os.path.join(RESOURCE, 'swedish.train.txt')} " \
                f"{os.path.join(RESOURCE, 'swedish.corp')} noweights " \
                f"{os.path.join(RESOURCE, 'threshold.swedish.elevtexter.txt')}".split(),
                capture_output = True
            )
            if response.returncode != 0:
                raise AnnotationError(f"Failed to normalize, {response.stderr}")
            write(filepath=output_file, context=response.stdout.decode())

        elif normalizer.lower() == "histnorm_en":
            enggram_spellcheck(filepath, output_file)

    except Exception as err:
        raise AnnotationError(f"Failed to normalize, {err}")
