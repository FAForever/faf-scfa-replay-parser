from replay_parser.replay import parse, get_body_parser


def test_replay_parse(replays):
    data = parse(replays)
    assert "header" in data
    assert "body" in data
    assert "body_offset" in data
    assert "messages" in data
    assert "desync_ticks" in data
    assert not data['desync_ticks'], data['desync_ticks']


def test_replay_header_parse(replays):
    data = parse(replays, parse_body=False)
    assert "header" in data
    assert "body" not in data
    assert "body_offset" in data
    assert "messages" not in data
    assert "desync_ticks" not in data


def test_continuous_parse(replays):
    parser = get_body_parser(replays, parse_header=True, parse_commands=[0, 3])
    for _ in parser.continuous_parse():
        pass


def test_parse_only_some_commands(replays):
    parse(replays, parse_commands=[x for x in range(23)])

