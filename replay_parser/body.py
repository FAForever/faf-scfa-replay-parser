from typing import List, Dict, Any

from replay_parser.commands import COMMAND_PARSERS
from replay_parser.config import DEBUG
from replay_parser.constants import CommandStates, CommandStateNames
from replay_parser.reader import ReplayReader

__all__ = ('ReplayBody',)


class ReplayBody:
    """
    Parses replay body.
    """

    def __init__(self, stream: ReplayReader, **kwargs) -> None:
        self.reader: ReplayReader = stream

        self.body: List = []
        self.last_players_tick: Dict = {}
        self.desync_ticks: List = []
        self.messages: Dict = {}

        self.tick: int = 0
        self.tick_data: Dict = {}
        self.player_id: int = -1

        self.previous_tick = -1
        self.previous_checksum = None
        self.parse_until_desync = kwargs.get('parse_until_desync', False)

    def get_body(self):
        return self.body

    def get_messages(self):
        return self.messages

    def get_last_players_ticks(self):
        return self.last_players_tick

    def get_desync_tics(self):
        return self.desync_ticks

    def parse(self) -> None:
        while self.reader.offset() < self.reader.size():
            if self.parse_until_desync and self.desync_ticks:
                break
            self.parse_next_command()

    def parse_next_command(self) -> None:
        command_type = self.reader.read_byte()
        command_length = self.reader.read_number(type_="h", size=2)
        command_parser = COMMAND_PARSERS[command_type]
        command_data = command_parser(self.reader)
        self.process_command(command_type, command_data)

        if DEBUG:
            print(self.reader.offset(), command_parser.__name__, command_type, command_length, "->", command_data)

    def process_command(self, command_type: int, command_data: Any) -> None:
        command_name = CommandStateNames[command_type]
        if command_type == CommandStates.Advance:
            if self.tick_data:
                self.body.append(self.tick_data)
            self.tick_data = {}
            self.tick += command_data
        elif command_type == CommandStates.SetCommandSource:
            self.player_id = command_data
        elif command_type == CommandStates.CommandSourceTerminated:
            self.last_players_tick[self.player_id] = self.tick
        elif command_type == CommandStates.VerifyChecksum:
            checksum, tick = command_data
            if tick == self.previous_tick and checksum != self.previous_checksum:
                self.desync_ticks.append(self.tick)
            self.previous_tick = tick
            self.previous_checksum = checksum
        elif command_type == CommandStates.LuaSimCallback:
            cmd_string, data = command_data
            if cmd_string == "GiveResourcesToPlayer" and "Msg" in data:
                self.messages[self.tick] = (data["Sender"], data["Msg"]["to"], data["Msg"]["text"])

        self.tick_data.setdefault(self.player_id, {})[command_name] = command_data
