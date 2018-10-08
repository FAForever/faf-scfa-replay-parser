import os
from io import BytesIO

import pytest

__all__ = ('replays', 'replay_file_name')

REPLAYS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "replays")


def get_replay_file_name():
    return [
        os.path.abspath(os.path.join(REPLAYS_DIR, file_name))
        for file_name in os.listdir(REPLAYS_DIR)
        if file_name.endswith(".scfareplay")
    ]


@pytest.fixture(params=get_replay_file_name())
def replay_file_name(request):
    return request.param


@pytest.fixture(params=[BytesIO, bytearray, bytes])
def replays(request, replay_file_name):
    output_type = request.param
    with open(replay_file_name, "rb") as f:
        return output_type(f.read())
