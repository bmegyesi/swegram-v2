"""Module of installation for efselab

See more information on https://github.com/robertostling/efselab
"""
import requests
import zipfile
from pathlib import Path

from build_dependencies.tools_conf import tool_folder


class EfselabError(Exception):
    """Efselab error. Check efselab on https://github.com/robertostling/efselab"""


def get_efselab(target_path: Path = Path(__file__).absolute().parent.parent):
    efselab_download_url = "https://github.com/robertostling/efselab/archive/refs/heads/master.zip"

    response = requests.get(efselab_download_url, stream=True)
    response.raise_for_status()
    import io
    with zipfile.ZipFile(io.BytesIO(response.content)) as zipobj:
        zipobj.extractall(path=target_path.joinpath(tool_folder))


if __name__ == "__main__":
    get_efselab()
