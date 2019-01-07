from typing import List, Dict, Any, Iterable

from replay_parser.commands import COMMAND_PARSERS
from replay_parser.config import DEBUG
from replay_parser.constants import CommandStates, CommandStateNames
from replay_parser.reader import ReplayReader

__all__ = ('ReplayBody',)


class ReplayBody:
    """
    Parses replay body.
    """
    def __init__(
            self,
            stream: ReplayReader,
            parse_until_desync: bool = False,
            parse_commands: set = None,
            store_body: bool = False,
            **kwargs
    ) -> None:
        """
        :param ReplayReader stream: Handles basic operations on stream
        :param bool parse_until_desync: stops parsing at first desync
        :param set parse_commands: set or list of commands ids to parse,
            list is defined in from `replay_parser.commands.COMMAND_PARSERS`.
            Important: you can't detect desyncs, if you won't have CommandStates.VerifyChecksum
        :param bool store_body: stores every next tick data of replay to content to self.body.
            To get list of commands use get_body
        """
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
        self.parse_until_desync = bool(parse_until_desync)
        self.parse_commands = set(parse_commands or set())
        self.store_body = bool(store_body)

    def get_body(self) -> List:
        return self.body

    def get_messages(self) -> Dict:
        return self.messages

    def get_last_players_ticks(self) -> Dict:
        return self.last_players_tick

    def get_desync_tics(self) -> List:
        return self.desync_ticks

    def parse(self) -> None:
        for _ in self.continuous_parse():
            pass

    def continuous_parse(self) -> Iterable:
        """
        Parses command until it can. Should be used as iterator.
        Yields game tick.

        replay format:
            1. byte for command 0-255
            2. 2 bytes for size of command 0 - 65,535
            3. content of command
        """
        while self.reader.offset() < self.reader.size():
            if self.parse_until_desync and self.desync_ticks:
                break
            read_length = 0
            command_type = self.reader.read_byte()
            if self.reader.offset() + 2 < self.reader.size():
                command_length = self.reader.read_short()

                if self.can_parse_command(command_type) and \
                   self.reader.offset() + command_length <= self.reader.size():
                    self.parse_next_command(command_type, command_length)
                else:
                    self.reader.read(command_length)
                read_length = command_length + 3  # read_byte + read_short + command_length
            yield self.tick, read_length

    def parse_next_command(self, command_type: int, command_length: int) -> None:
        command_parser = COMMAND_PARSERS[command_type]
        command_data = command_parser(self.reader)
        self.process_command(command_type, command_data)

        if DEBUG:
            print(self.reader.offset(), command_parser.__name__, command_type, command_length, "->", command_data)

    def process_command(self, command_type: int, command_data: Any) -> None:
        command_name = CommandStateNames[command_type]
        if command_type == CommandStates.Advance:
            if self.store_body and self.tick_data:
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

        if self.store_body:
            self.tick_data.setdefault(self.player_id, {})[command_name] = command_data

    def can_parse_command(self, command_type):
        return not self.parse_commands or command_type in self.parse_commands
