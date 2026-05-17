import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from swegram_main.lib.logger import get_logger

UDPIPE_REPO = "https://github.com/ufal/udpipe.git"
logger = get_logger(__name__)
workspace = os.path.abspath(os.path.dirname(__file__))
udpipe = Path(workspace).joinpath("en", "udpipe")


def install_udpipe():
    """Install udpipe"""
    if not udpipe.exists():
        logger.info("Start installing udpipe")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download udpipe repository
            response = subprocess.run(
                f"git clone {UDPIPE_REPO} {temp_dir}".split(),
                capture_output=True
            )
            if response.returncode != 0:
                raise Exception(f"Failed to clone udpipe repo: {response.stderr}")
            # Compiling udpipe model
            logger.info("Compiling...")
            os.chdir(os.path.join(temp_dir, "src"))
            response = subprocess.run(
                ["make"], capture_output=True
            )
            if response.returncode != 0:
                raise Exception(f"Faied to compiling udpipe: {response.stderr}")
            # Copy udpipe model to be folder
            shutil.copy(os.path.join(temp_dir, "src", "udpipe"), udpipe)
            logger.info("Successfully installed udpipe model.")


def main():
    install_udpipe()


if __name__ == "__main__":
    main()
