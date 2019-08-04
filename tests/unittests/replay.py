from io import BytesIO

from constants import CommandStates
from replay_parser.body import ReplayBody
from replay_parser.reader import ReplayReader
from replay_parser.replay import continuous_parse, parse


def test_replay_parse(replays, replay_file_name):
    data = parse(
        replays,
        parse_commands={
            CommandStates.Advance,
            CommandStates.SetCommandSource,
            CommandStates.CommandSourceTerminated,
            CommandStates.VerifyChecksum,
        }
    )
    assert "header" in data
    assert "body" in data
    assert "body_offset" in data
    assert "messages" in data
    assert "desync_ticks" in data
    assert "last_tick" in data
    if "8748707" in replay_file_name:
        assert 9105 in data['desync_ticks'], data['desync_ticks']
    else:
        assert not data['desync_ticks'], data['desync_ticks']


def test_replay_header_parse(replays):
    data = parse(replays, parse_body=False)
    assert "header" in data
    assert "body" not in data
    assert "body_offset" in data
    assert "messages" not in data
    assert "desync_ticks" not in data
    assert "last_tick" not in data


def test_parse_only_some_commands(replays):
    parse(replays, parse_commands=[x for x in range(23)])


def test_continuous_parse_command_by_command(replays):
    sender_stream = continuous_parse(
        replays,
        parse_header=True,
        parse_commands={
            CommandStates.Advance,
            CommandStates.SetCommandSource,
            CommandStates.CommandSourceTerminated,
            CommandStates.VerifyChecksum,
        }
    )
    server_body_buffer = BytesIO()
    server_body_parser = ReplayBody(
        ReplayReader(server_body_buffer),
        parse_commands={x for x in range(7)}
    )
    header = next(sender_stream)

    assert "header" in header
    assert "body_offset" in header
    for tick, command_type, data in sender_stream:
        times = 0
        for tick2, command_type2, data2 in server_body_parser.continuous_parse(data):
            assert tick == tick2
            assert command_type == command_type2
            assert data == data2
            times += 1

        assert times == 1


def test_parse_until_desync(replays):
    parse(replays, stop_on_desync=True)


def test_parse_only_ticks(replays):
    data = parse(replays, parse_commands=[CommandStates.Advance])
    assert data['last_tick']
