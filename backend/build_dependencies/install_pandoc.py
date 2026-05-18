"""Module of installation for pandoc

"""
import requests
import tarfile
from pathlib import Path

from build_dependencies.tools_conf import tool_folder


pandoc_version = "2.19.2"


class PandocError(Exception):
    """Pandoc error. Check pandoc on https://pandoc.org"""


def get_pandoc(target_path: Path = Path(__file__).absolute().parent.parent):
    pandoc_download_url = "https://github.com/jgm/pandoc/releases/download/" \
                          f"{pandoc_version}/pandoc-{pandoc_version}-linux-amd64.tar.gz"

    response = requests.get(pandoc_download_url, stream=True)
    response.raise_for_status()

    with tarfile.open(fileobj=response.raw, mode="r:gz") as tarobj:
        tarobj.extractall(path=target_path.joinpath(tool_folder))


if __name__ == "__main__":
    get_pandoc()
