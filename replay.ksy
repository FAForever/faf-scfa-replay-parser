# kaitai struct was taken from Crotalus repo https://gist.github.com/Crotalus/c003ddb0e3802b30a5740e81e0f8ae65
meta:
  id: scfa_replay
  file-extension: scfareplay
  encoding: utf-8
  endian: le

seq:
  - id: header
    type: header
  - id: op_stream
    type: op_stream

types:
  replay_map:
    seq:
      - id: replay
        type: strz

  formation_data:
    seq:
      - id: w
        type: f4
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: scale
        type: f4

  formation:
    seq:
        - id: id
          type: s4
        - id: data
          type: formation_data
          if: id != -1

  position:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  target:
    seq:
      - id: target_type
        type: u1
      - id: entity
        type: u4
        if: target_type == 1
      - id: position
        type: position
        if: target_type == 2

  # general types

  luakv:
    seq:
      - id: key
        type: lua
      - id: value
        type: lua
        if: key.type != luatype::end

  luatable:
    seq:
      - id: data
        type: luakv
        repeat: until
        repeat-until: _.key.type == luatype::end

  lua:
    seq:
      - id: type
        type: u1
        enum: luatype

      - id: data
        if: type != luatype::end
        type:
          switch-on: type
          cases:
            'luatype::float': f4
            'luatype::string': strz
            'luatype::nil': u1
            'luatype::bool': u1
            'luatype::table': luatable
  timeout:
    seq:
      - id: player
        type: strz
      - id: timeouts_left
        type: u4

  playerdata:
    seq:
      - id: size
        type: u4
      - id: data
        type: lua
      - id: source
        type: u1
      - id: unknown
        type: u1
        if: source != 255

  header:
    seq:
    - id: name
      type: strz
      encoding: utf8
    - id: unknown
      type: strz
      encoding: utf8
    - id: replay_version
      type: str
      terminator: 10
    - id: map_file
      type: strz
    - id: unknown2
      type: u4
    - id: num_mods
      type: u4
    - id: mods
      type: lua
    - id: scenario_size
      type: u4
    - id: scenario
      type: lua
    - id: num_sources
      type: u1
    - id: timeouts
      type: timeout
      repeat: expr
      repeat-expr: num_sources
    - id: cheats
      type: u1
    - id: num_armies
      type: u1
    - id: player_data
      type: playerdata
      repeat: expr
      repeat-expr: num_armies
    - id: random_seed
      type: u4

  op:
    seq:
    - id: type
      type: u1
      enum: optype
    - id: len
      type: u2
    - id: data
      size: len - 3
      type:
        switch-on: type
        cases:
          'optype::advance': op_advance
          'optype::set_command_source': op_set_command_source
          'optype::verify_checksum': op_verify_checksum
          'optype::request_pause': op_request_pause
          'optype::resume': op_request_resume
          'optype::issue_command': op_issue_command
          'optype::issue_factory_command': op_issue_command
          'optype::lua_sim_callback': op_lua_sim_callback

  op_advance:
    seq:
      - id: num_ticks
        type: u4

  op_set_command_source:
    seq:
      - id: source
        type: u1

  op_command_source_terminated:
    seq:
      - id: source
        type: u1

  op_verify_checksum:
    seq:
      - id: checksum
        size: 20

  op_request_pause:
    seq:
      - id: source
        type: u1

  op_request_resume:
    seq:
      - id: source
        type: u1

  op_issue_command:
    seq:
      - id: num_units
        type: u4
      - id: unit_ids
        type: u4
        repeat: expr
        repeat-expr: num_units
      - id: cmd_id
        type: u4
      - id: unknown
        type: u4
      - id: cmd_type
        type: u1
      - id: unknown2
        type: u4
      - id: target
        type: target
      - id: unknown3
        type: u1
      - id: formation
        type: formation
      - id: bp
        type: strz
      - id: unknown4
        size: 12
      - id: lua
        type: lua
      - id: unknown5
        type: u1
        if: lua.type != luatype::nil

  op_lua_sim_callback:
      seq:
      - id: name
        type: strz
      - id: lua
        type: lua
      - id: unknown
        type: u4
        if: lua.type != luatype::nil
      - id: skip_if_lua
        type: u4
        repeat: expr
        repeat-expr: unknown
        if: lua.type != luatype::nil
      - id: skip_if_not_lua
        size: 7
        if: lua.type == luatype::nil

  op_stream:
    seq:
      - id: ops
        type: op
        repeat: eos

enums:
  luatype:
    0: float
    1: string
    2: nil
    3: bool
    4: table
    5: end

  optype:
    0: advance
    1: set_command_source
    2: command_source_terminated
    3: verify_checksum
    4: request_pause
    5: resume
    6: single_step
    7: create_unit
    8: create_prop
    9: destroy_entity
    10: warp_entity
    11: process_info_pair
    12: issue_command
    13: issue_factory_command
    14: increase_command_count
    15: decrease_command_count
    16: set_command_target
    17: set_command_type
    18: set_command_cells
    19: remove_command_from_queue
    20: debug_command
    21: execute_lua_in_sim
    22: lua_sim_callback
    23: end_game