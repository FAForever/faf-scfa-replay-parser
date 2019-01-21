# cython: language_level=3

from typing import Tuple, Optional, List

from replay_parser.constants import TargetType, CommandStates
from replay_parser.reader import ReplayReader, TYPE_LUA

__all__ = ('COMMAND_PARSERS',)


TYPE_VECTOR = Tuple[float, float, float]
TYPE_FORMATION = Optional[Tuple[float, float, float, float, float]]
TYPE_TARGET = Tuple[int, Optional[int], Optional[TYPE_VECTOR]]
TYPE_COMMAND_DATA = Tuple[int, int, TYPE_TARGET, TYPE_FORMATION, str, TYPE_LUA]


def _read_vector(reader: ReplayReader) -> TYPE_VECTOR:
    return reader.read_float(), reader.read_float(), reader.read_float()


def command_nop(reader: ReplayReader) -> None:
    """
    No operation. Shortcut for some commands
    """
    return None


def command_advance(reader: ReplayReader) -> int:
    return reader.read_int()


def command_set_command_source(reader: ReplayReader) -> int:
    return reader.read_byte()


def command_verify_checksum(reader: ReplayReader) -> Tuple[str, int]:
    checksum = "".join("{:02X}".format(ord(reader.read(1))) for _ in range(16))
    return checksum, reader.read_int()


def command_create_unit(reader: ReplayReader) -> Tuple[int, str, TYPE_VECTOR]:
    army_index = reader.read_byte()
    blueprint_id = reader.read_string()
    x, y, heading = _read_vector(reader)
    return army_index, blueprint_id, (x, y, heading)


def command_create_prop(reader: ReplayReader) -> Tuple[str, TYPE_VECTOR]:
    return reader.read_string(), _read_vector(reader)


def command_destroy_entity(reader: ReplayReader) -> int:
    return reader.read_int()


def command_warp_entity(reader: ReplayReader) -> Tuple[int, TYPE_VECTOR]:
    return reader.read_int(), _read_vector(reader)


def command_process_info_pair(reader: ReplayReader) -> Tuple[int, str, str]:
    entity_id = reader.read_int()
    arg1 = reader.read_string()
    arg2 = reader.read_string()
    return entity_id, arg1, arg2


def _parse_entity_ids_set(reader: ReplayReader) -> Tuple[int, List[int]]:
    units_number = reader.read_int()
    unit_ids = []
    for i in range(units_number):
        unit_ids.append(reader.read_int())
    return units_number, unit_ids


def _parse_formation(reader: ReplayReader) -> TYPE_FORMATION:
    formation = reader.read_int()
    if formation != -1:
        w = reader.read_float()
        x, y, z = _read_vector(reader)
        scale = reader.read_float()
        return w, x, y, z, scale
    return None


def _parse_target(reader: ReplayReader) -> TYPE_TARGET:
    target = reader.read_byte()
    entity_id = None
    position = None
    if target == TargetType.Entity:
        entity_id = reader.read_int()
    elif target == TargetType.Position:
        x = reader.read_float()
        y = reader.read_float()
        z = reader.read_float()
        position = x, y, z
    return target, entity_id, position


def _parse_command_data(reader: ReplayReader) -> TYPE_COMMAND_DATA:
    command_id = reader.read_int()
    reader.read(4)
    command_type = reader.read_byte()
    reader.read(4)

    sti_target = _parse_target(reader)

    reader.read(1)
    formation = _parse_formation(reader)

    blueprint_id = reader.read_string()

    reader.read(12)
    cells = reader.read_lua()
    if cells:
        reader.read(1)

    return command_id, command_type, sti_target, formation, blueprint_id, cells


def command_issue(reader: ReplayReader) -> Tuple[int, List[int], TYPE_COMMAND_DATA]:
    units_number, unit_ids = _parse_entity_ids_set(reader)
    cmd_data = _parse_command_data(reader)

    return units_number, unit_ids, cmd_data


def command_command_count(reader: ReplayReader) -> Tuple[int, int]:
    return reader.read_int(), reader.read_int()


def command_set_command_target(reader: ReplayReader) -> Tuple[int, TYPE_TARGET]:
    return reader.read_int(), _parse_target(reader)


def command_set_command_type(reader: ReplayReader) -> Tuple[int, int]:
    return reader.read_int(), reader.read_int()


def command_set_command_cells(reader: ReplayReader) -> Tuple[int, TYPE_LUA, TYPE_VECTOR]:
    command_id = reader.read_int()
    cells = reader.read_lua()
    if cells:
        reader.read(1)
    vector = (reader.read_float(), reader.read_float(), reader.read_float())
    return command_id, cells, vector


def command_remove_from_queue(reader: ReplayReader) -> Tuple[int, int]:
    return reader.read_int(), reader.read_int()


def command_debug_command(reader: ReplayReader) -> Tuple[str, TYPE_VECTOR, int, List[int]]:
    debug_command = reader.read_string()
    vector = _read_vector(reader)
    focus_army_index = reader.read_byte()
    _, unit_ids = _parse_entity_ids_set(reader)
    return debug_command, vector, focus_army_index, unit_ids


def command_execute_lua_in_sim(reader: ReplayReader) -> str:
    return reader.read_string()


def command_lua_sim_callback(reader: ReplayReader) -> Tuple[str, TYPE_LUA]:
    lua_name = reader.read_string()
    lua = reader.read_lua()
    if lua:
        size = reader.read_int()
        reader.read(4 * size)
    else:
        reader.read(4 + 3)

    return lua_name, lua


COMMAND_PARSERS = {
    CommandStates.Advance: command_advance,
    CommandStates.SetCommandSource: command_set_command_source,
    CommandStates.CommandSourceTerminated: command_nop,
    CommandStates.VerifyChecksum: command_verify_checksum,
    CommandStates.RequestPause: command_nop,
    CommandStates.Resume: command_nop,
    CommandStates.SingleStep: command_nop,
    CommandStates.CreateUnit: command_create_unit,
    CommandStates.CreateProp: command_create_prop,
    CommandStates.DestroyEntity: command_destroy_entity,
    CommandStates.WarpEntity: command_warp_entity,
    CommandStates.ProcessInfoPair: command_process_info_pair,
    CommandStates.IssueCommand: command_issue,
    CommandStates.IssueFactoryCommand: command_issue,
    CommandStates.IncreaseCommandCount: command_command_count,
    CommandStates.DecreaseCommandCount: command_command_count,
    CommandStates.SetCommandTarget: command_set_command_target,
    CommandStates.SetCommandType: command_set_command_type,
    CommandStates.SetCommandCells: command_set_command_cells,
    CommandStates.RemoveCommandFromQueue: command_remove_from_queue,
    CommandStates.DebugCommand: command_debug_command,
    CommandStates.ExecuteLuaInSim: command_execute_lua_in_sim,
    CommandStates.LuaSimCallback: command_lua_sim_callback,
    CommandStates.EndGame: command_nop,
}
