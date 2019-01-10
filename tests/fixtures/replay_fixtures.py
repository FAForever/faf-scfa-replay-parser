import os
from io import BytesIO, FileIO

import pytest

__all__ = ('replays', 'replay_file_name')

REPLAYS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "replays")


def get_replay_file_name():
    """
    Iterate over replay in fixtures directory
    """
    return [
        os.path.abspath(os.path.join(REPLAYS_DIR, file_name))
        for file_name in os.listdir(REPLAYS_DIR)
        if file_name.endswith(".scfareplay")
    ]


@pytest.fixture(params=get_replay_file_name())
def replay_file_name(request):
    """
    Returns file names from parametrized request
    """
    return request.param


@pytest.fixture(params=[BytesIO, bytearray, bytes, FileIO])
def replays(request, replay_file_name):
    output_type = request.param
    if issubclass(output_type, FileIO):
        return FileIO(replay_file_name, "rb")

    with open(replay_file_name, "rb") as f:
        return output_type(f.read())
