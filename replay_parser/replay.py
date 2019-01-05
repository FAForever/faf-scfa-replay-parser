from io import RawIOBase
from typing import Union, Dict, Any

from replay_parser.body import ReplayBody
from replay_parser.header import ReplayHeader
from replay_parser.reader import ReplayReader

__all__ = ('parse', 'get_body_parser',)


def parse(
        input_data: Union[RawIOBase, bytearray, bytes],
        parse_body: bool=True,
        **kwargs
) -> Dict[str, Any]:
    """
    Parses replay

    :param (RawIOBase, bytearray, bytes) input_data: data source
    :param bool parse_body: define what to parse
    """
    reader = ReplayReader(input_data, **kwargs)
    result = {
        "header": ReplayHeader(reader).to_dict(),
        "body_offset": reader.offset(),
    }

    if parse_body:
        body_parser = ReplayBody(reader, **kwargs)
        body_parser.parse()
        result["body"] = body_parser.get_body()
        result["messages"] = body_parser.get_messages()
        result["desync_ticks"] = body_parser.get_desync_tics()

    return result


def get_body_parser(
        input_data: Union[RawIOBase, bytearray, bytes],
        parse_header=False,
        **kwargs
) -> ReplayBody:
    """
    Used for continuous replay body parsing, when header is not needed.
    Returns `ReplayBody` parser, that has `continuous_parse`.

    Example:
    ::
        >>> reader = ReplayReader(FileIO(input_data))
        >>> ReplayHeader(reader)  # jump over header
        >>> for row in ReplayBody(reader).continuous_parse(): pass
    """
    reader = ReplayReader(input_data, **kwargs)
    if parse_header:
        ReplayHeader(reader)

    return ReplayBody(reader, **kwargs)
