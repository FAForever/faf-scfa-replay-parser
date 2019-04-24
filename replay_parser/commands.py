from typing import Tuple, Optional, List, Dict, Union

from replay_parser.constants import TargetType, CommandStates
from replay_parser.reader import ReplayReader, TYPE_LUA

__all__ = ('COMMAND_PARSERS',)


TYPE_VECTOR = Tuple[float, float, float]
TYPE_FORMATION = Optional[Dict[str, Union[float, TYPE_VECTOR]]]
TYPE_TARGET = Dict[str, Union[int, TYPE_VECTOR]]
TYPE_COMMAND_DATA = Dict[str, Union[int, bytes, TYPE_TARGET, TYPE_FORMATION]]
TYPE_ENTITY_IDS_SET = Dict[str, Union[int, List[int]]]


def _read_vector(reader: ReplayReader) -> TYPE_VECTOR:
    return reader.read_float(), reader.read_float(), reader.read_float()


def command_advance(reader: ReplayReader) -> Dict[str, int]:
    return {"type": "advance",
            "advance": reader.read_int()}


def command_set_command_source(reader: ReplayReader) -> Dict[str, int]:
    return {"type": "set_command_source",
            "player_id": reader.read_byte()}


def command_source_terminated(reader: ReplayReader) -> Dict:
    return {"type": "command_source_terminated"}


def command_verify_checksum(reader: ReplayReader) -> Dict[str, Union[str, int]]:
    checksum = "".join("{:02X}".format(ord(reader.read(1))) for _ in range(16))
    return {"type": "verify_checksum",
            "checksum": checksum,
            "tick": reader.read_int()}


def command_request_pause(reader: ReplayReader) -> Dict:
    return {"type": "request_pause"}


def command_resume(reader: ReplayReader) -> Dict:
    return {"type": "resume"}


def command_single_step(reader: ReplayReader) -> Dict:
    return {"type": "single_step"}


def command_create_unit(reader: ReplayReader) -> Dict[str, Union[int, str, TYPE_VECTOR]]:
    army_index = reader.read_byte()
    blueprint_id = reader.read_string()
    x, y, heading = _read_vector(reader)
    return {"type": "create_unit",
            "army_index": army_index,
            "blueprint_id": blueprint_id,
            "vector": (x, y, heading)}


def command_create_prop(reader: ReplayReader) -> Dict[str, Union[str, TYPE_VECTOR]]:
    return {"type": "create_prop",
            "name": reader.read_string(),
            "vector": _read_vector(reader)}


def command_destroy_entity(reader: ReplayReader) -> Dict[str, int]:
    return {"type": "destroy_entity",
            "entity_id": reader.read_int()}


def command_warp_entity(reader: ReplayReader) -> Dict[str, Union[str, TYPE_VECTOR]]:
    return {"type": "warp_entity",
            "entity_id": reader.read_int(),
            "vector": _read_vector(reader)}


def command_process_info_pair(reader: ReplayReader) -> Dict[str, Union[int, str]]:
    entity_id = reader.read_int()
    arg1 = reader.read_string()
    arg2 = reader.read_string()
    return {"type": "process_info_pair",
            "entity_id": entity_id,
            "arg1": arg1,
            "arg2": arg2}


def _parse_entity_ids_set(reader: ReplayReader) -> TYPE_ENTITY_IDS_SET:
    units_number = reader.read_int()
    unit_ids = []
    for i in range(units_number):
        unit_ids.append(reader.read_int())
    return {"units_number": units_number, "unit_ids": unit_ids}


def _parse_formation(reader: ReplayReader) -> TYPE_FORMATION:
    formation = reader.read_int()
    if formation != -1:
        w = reader.read_float()
        position = _read_vector(reader)
        scale = reader.read_float()
        return {"w": w, "position": position, "scale": scale}
    return None


def _parse_target(reader: ReplayReader) -> TYPE_TARGET:
    target = reader.read_byte()
    entity_id = None
    position = None
    if target == TargetType.Entity:
        entity_id = reader.read_int()
    elif target == TargetType.Position:
        position = _read_vector(reader)
    return {"target": target, "entity_id": entity_id, "position": position}


def _parse_command_data(reader: ReplayReader) -> TYPE_COMMAND_DATA:
    command_id = reader.read_int()
    arg1 = reader.read(4)
    command_type = reader.read_byte()
    arg2 = reader.read(4)

    target = _parse_target(reader)

    arg3 = reader.read(1)
    formation = _parse_formation(reader)

    blueprint_id = reader.read_string()

    arg4 = reader.read(12)
    arg5 = None
    cells = reader.read_lua()
    if cells:
        arg5 = reader.read(1)

    return {"command_id": command_id,
            "command_type": command_type,
            "target": target,
            "formation": formation,
            "blueprint_id": blueprint_id,
            "cells": cells,
            "arg1": arg1,
            "arg2": arg2,
            "arg3": arg3,
            "arg4": arg4,
            "arg5": arg5}


def command_issue(reader: ReplayReader) -> Dict[str, Union[str, int, List[int], TYPE_COMMAND_DATA]]:
    unit_ids = _parse_entity_ids_set(reader)
    cmd_data = _parse_command_data(reader)

    return {"type": "issue",
            "entity_ids_set": unit_ids,
            "cmd_data": cmd_data}


def command_factory_issue(reader: ReplayReader) -> Dict[str, Union[str, int, List[int], TYPE_COMMAND_DATA]]:
    unit_ids = _parse_entity_ids_set(reader)
    cmd_data = _parse_command_data(reader)

    return {"type": "factory_issue",
            "entity_ids_set": unit_ids,
            "cmd_data": cmd_data}


def command_command_count_increase(reader: ReplayReader) -> Dict[str, Union[str, int]]:
    return {"type": "command_count_increase",
            "command_id": reader.read_int(),
            "delta": reader.read_int()}


def command_command_count_decrease(reader: ReplayReader) -> Dict[str, Union[str, int]]:
    return {"type": "command_count_decrease",
            "command_id": reader.read_int(),
            "delta": reader.read_int()}


def command_set_command_target(reader: ReplayReader) -> Dict[str, Union[int, TYPE_TARGET]]:
    return {"type": "set_command_target",
            "command_id": reader.read_int(),
            "target": _parse_target(reader)}


def command_set_command_type(reader: ReplayReader) -> Dict[str, Union[str, int]]:
    return {"type": "set_command_type",
            "command_id": reader.read_int(),
            "target_id": reader.read_int()}


def command_set_command_cells(reader: ReplayReader) -> Dict[str, Union[str, int, TYPE_LUA]]:
    command_id = reader.read_int()
    cells = reader.read_lua()
    if cells:
        reader.read(1)
    vector = (reader.read_float(), reader.read_float(), reader.read_float())
    return {"type": "set_command_cells",
            "command_id": command_id,
            "cells": cells,
            "vector": vector}


def command_remove_from_queue(reader: ReplayReader) -> Dict[str, int]:
    return {"type": "remove_from_queue",
            "command_id": reader.read_int(),
            "unit_id": reader.read_int()}


def command_debug_command(reader: ReplayReader) -> Dict[str, Union[str, TYPE_VECTOR, int, TYPE_ENTITY_IDS_SET]]:
    debug_command = reader.read_string()
    vector = _read_vector(reader)
    focus_army_index = reader.read_byte()
    unit_ids = _parse_entity_ids_set(reader)
    return {"type": "debug_command",
            "debug_command": debug_command,
            "vector": vector,
            "focus_army_index": focus_army_index,
            "entity_ids_set": unit_ids}


def command_execute_lua_in_sim(reader: ReplayReader) -> Dict[str, str]:
    return {"type": "execute_lua_in_sim",
            "lua": reader.read_string()}


def command_lua_sim_callback(reader: ReplayReader) -> Dict[str, Union[str, TYPE_LUA, bytes]]:
    lua_name = reader.read_string()
    lua = reader.read_lua()
    size = None
    data = None
    if lua:
        size = reader.read_int()
        data = reader.read(4 * size)
    else:
        data = reader.read(4 + 3)

    return {"type": "lua_sim_callback",
            "lua_name": lua_name,
            "lua": lua,
            "size": size,
            "data": data}


def command_end_game(reader: ReplayReader) -> Dict:
    return {"type": "end_game"}


COMMAND_PARSERS = {
    CommandStates.Advance: command_advance,
    CommandStates.SetCommandSource: command_set_command_source,
    CommandStates.CommandSourceTerminated: command_source_terminated,
    CommandStates.VerifyChecksum: command_verify_checksum,
    CommandStates.RequestPause: command_request_pause,
    CommandStates.Resume: command_resume,
    CommandStates.SingleStep: command_single_step,
    CommandStates.CreateUnit: command_create_unit,
    CommandStates.CreateProp: command_create_prop,
    CommandStates.DestroyEntity: command_destroy_entity,
    CommandStates.WarpEntity: command_warp_entity,
    CommandStates.ProcessInfoPair: command_process_info_pair,
    CommandStates.IssueCommand: command_issue,
    CommandStates.IssueFactoryCommand: command_factory_issue,
    CommandStates.IncreaseCommandCount: command_command_count_increase,
    CommandStates.DecreaseCommandCount: command_command_count_decrease,
    CommandStates.SetCommandTarget: command_set_command_target,
    CommandStates.SetCommandType: command_set_command_type,
    CommandStates.SetCommandCells: command_set_command_cells,
    CommandStates.RemoveCommandFromQueue: command_remove_from_queue,
    CommandStates.DebugCommand: command_debug_command,
    CommandStates.ExecuteLuaInSim: command_execute_lua_in_sim,
    CommandStates.LuaSimCallback: command_lua_sim_callback,
    CommandStates.EndGame: command_end_game,
}
