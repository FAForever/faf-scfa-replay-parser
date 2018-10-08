from io import RawIOBase
from typing import Union, Dict, Any

from replay_parser.body import ReplayBody
from replay_parser.header import ReplayHeader
from replay_parser.reader import ReplayReader

NEW_LINE = "\r\n"

__all__ = ('parse',)


def parse(input_data: Union[RawIOBase, bytearray, bytes], **kwargs) -> Dict[str, Any]:
    """
    Parses replay
    """
    reader = ReplayReader(input_data)
    header = ReplayHeader(reader).to_dict()
    offset = reader.offset()
    body_parser = ReplayBody(reader, **kwargs)
    body_parser.parse()
    return {
        "header": header,
        "body": body_parser.get_body(),
        "body_offset": offset,
        "messages": body_parser.get_messages(),
        "desync_ticks": body_parser.get_desync_tics(),
    }
