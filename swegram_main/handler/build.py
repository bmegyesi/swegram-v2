
import os
import sys
import subprocess

from swegram_main.config import BASE_DIR
from swegram_main.lib.logger import get_logger


logger = get_logger(__file__)
sys.path.insert(1, BASE_DIR)
sys.path.insert(1, BASE_DIR.joinpath("tools", "efselab"))


def main():
    try:
        swegram_workspace = os.environ["SWEGRAM_WORKSPACE"]
        logger.info(f"SWEGRAM_WORKSPACE: {swegram_workspace}")
    except KeyError:
        raise Exception("Environment SWEGRAM_WORKSPACE is not set.")

    if BASE_DIR.joinpath("tools").exists():
        logger.info("Remove tools")
        subprocess.run(f"rm -rf {BASE_DIR.joinpath('tools')}".split())
    logger.info("Install tools")
    subprocess.run(f"{BASE_DIR.joinpath('build_dependencies', 'install.sh')}".split())
