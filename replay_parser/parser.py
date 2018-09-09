from io import RawIOBase, BytesIO
from struct import unpack
from typing import Union, Dict, Any, Tuple

from .constants import LuaType

NEW_LINE = "\r\n"


def read_string(data: bytearray, offset: int) -> Tuple[str, int]:
    """
    Parses string from binary data.
    """
    res = b""
    while True:
        char_ = unpack("s", data[offset:offset + 1])[0]
        offset += 1

        if char_ == b'\x00':
            break
        res += char_
    return res.decode(), offset


def read_number(data: bytearray, offset: int, type_: str = "i", size: int = 4) -> Tuple[Union[int, float], int]:
    """
    Reads number/float/boolean by input type & size
    """
    value = unpack(type_, data[offset:offset + size])[0]
    return value, offset + size


def read_lua_format(data: bytearray, offset: int) -> Tuple[Union[int, float, str, bool, None, dict], int]:
    """
    Reads struct format
    """
    type_, offset = read_number(data, offset, type_="b", size=1)

    if type_ == LuaType.NUMBER:
        return read_number(data, offset, type_="f", size=4)
    elif type_ == LuaType.STRING:
        return read_string(data, offset)
    elif type_ == LuaType.NIL:
        return None, offset + 1
    elif type_ == LuaType.BOOL:
        value, offset = read_number(data, offset, type_="b", size=1)
        return value == 1, offset
    elif type_ == LuaType.LUA:
        result = {}

        while True:
            value, offset = read_number(data, offset, type_="b", size=1)
            if value == LuaType.LUA_END:
                break

            offset -= 1
            key, offset = read_lua_format(data, offset)
            value, offset = read_lua_format(data, offset)
            result[key] = value
        return result, offset
    return None, offset


def parse(input_data: Union[RawIOBase, bytearray, bytes]) -> Dict[str, Any]:
    """
    Parses replay
    """
    data = None
    if isinstance(input_data, RawIOBase):
        # get data and move back to previous position
        position = input_data.tell()
        input_data.seek(0)
        data = input_data.read()  # copy as bytes
        input_data.seek(position)
    elif isinstance(input_data, bytes):
        data = bytearray(input_data)  # copy data

    header, offset = parse_header(data)
    body, offset = parse_body(data, offset)
    return {'header': header, "body": body, "body_offset": offset}


def parse_header(data: bytearray):
    """
    Parses replay header
    """
    offset = 0
    version, offset = read_string(data, offset)
    offset += 3
    replay_version_and_map, offset = read_string(data, offset)
    replay_version, map_name = replay_version_and_map.split(NEW_LINE, 2)
    offset += 4
    mods_size, offset = read_number(data, offset)
    mods, offset = read_lua_format(data, offset)
    scenario_size, offset = read_number(data, offset)
    scenario, offset = read_lua_format(data, offset)
    sources_number, offset = read_number(data, offset, type_="b", size=1)

    players = {}
    for i in range(sources_number):
        name, offset = read_string(data, offset)
        player_id, offset = read_number(data, offset)
        players[name] = str(player_id)

    cheats_enabled, offset = read_number(data, offset, type_="b", size=1)
    numbers_of_armies, offset = read_number(data, offset, type_="b", size=1)

    armies = {}
    for i in range(numbers_of_armies):
        player_data_size, offset = read_number(data, offset, size=4)
        player_data, offset = read_lua_format(data, offset)
        player_source, offset = read_number(data, offset, type_="b", size=1)
        armies[player_source] = player_data

        if player_source != 255:
            offset += 1

    random_seed, offset = read_number(data, offset, type_="f", size=4)

    header = {
        "version": version,
        "replay_version": replay_version,
        "map_name": map_name,
        "mods": mods,
        "scenario": scenario,
        "players": players,
        "cheats_enabled": cheats_enabled,
        "numbers_of_armies": numbers_of_armies,
        "armies": armies,
    }

    return header, offset


def parse_body(data: bytearray, offset: int):
    """
    TODO: implement if you need it
    """
    body = []
    return body, offset
