# cython: language_level=3

from typing import Dict

from replay_parser.reader import ReplayReader


class ReplayHeader:
    """
    Represents replay header structure.
    """

    __slots__ = (
        "version", "replay_version", "map_name", "mods", "scenario",
        "players", "cheats_enabled", "numbers_of_armies", "armies",
        "random_seed"
    )

    def __init__(self, reader: ReplayReader) -> None:
        self.version = reader.read_string()
        reader.read(3)
        self.replay_version, self.map_name = reader.read_string().split("\r\n", 1)
        reader.read(4)

        mods_size = reader.read_int()
        self.mods = reader.read_lua()
        scenario_size = reader.read_int()
        self.scenario = reader.read_lua()
        sources_number = reader.read_byte()

        self.players = {}
        for i in range(sources_number):
            name = reader.read_string()
            player_id = reader.read_int()
            self.players[name] = str(player_id)

        self.cheats_enabled = reader.read_bool()
        self.numbers_of_armies = reader.read_byte()

        self.armies = {}
        for i in range(self.numbers_of_armies):
            player_data_size = reader.read_int()
            player_data = reader.read_lua()
            player_source = reader.read_byte()
            self.armies[player_source] = player_data

            if player_source != 255:
                reader.read(1)

        self.random_seed = reader.read_float()

    def to_dict(self) -> Dict:
        ret = {}
        for key_name in self.__slots__:
            ret[key_name] = getattr(self, key_name)
        return ret
