
__all__ = (
    'DataType',
    'TargetType',
    'CommandStates',
    'ActionType',
    'CommandStateNames',
)


class DataType:
    """
    Defines type for stream
    """
    NUMBER = 0
    STRING = 1
    NIL = 2
    BOOL = 3
    LUA = 4  # dict
    LUA_END = 5


class TargetType:
    NONE = 0
    Entity = 1
    Position = 2


class CommandStates:
    # uint32 - number of beats to advance.
    Advance = 0

    # uint8 - command source
    SetCommandSource = 1

    # no args.
    CommandSourceTerminated = 2

    # MD5Digest - checksum
    # uint32 - beat number
    VerifyChecksum = 3

    # All with no additional data.
    RequestPause = 4
    Resume = 5
    SingleStep = 6

    # uint8 - army index
    # string - blueprint ID
    # float - x
    # float - z
    # float - heading
    CreateUnit = 7

    # string - blueprint ID
    # Vector3f - location
    CreateProp = 8

    # EntId - entity
    DestroyEntity = 9

    # EntId - entity
    # VTransform - new transform
    WarpEntity = 10

    # EntId - entity
    # string - arg1
    # string - arg2
    ProcessInfoPair = 11

    # uint32 - num units
    # EntIdSet - units
    # CmdData - command data
    # uint8 - clear queue flag
    IssueCommand = 12

    # uint32 - num factories
    # EntIdSet - factories
    # CmdData - command data
    # uint8 - clear queue flag
    IssueFactoryCommand = 13

    # CmdId - command id
    # int32 - count delta
    IncreaseCommandCount = 14

    # CmdId - command id
    # int32 - count delta
    DecreaseCommandCount = 15

    # CmdId - command id
    # STITarget - target
    SetCommandTarget = 16

    # CmdId - command id
    # EUnitCommandType - type
    SetCommandType = 17

    # CmdId - command id
    # ListOfCells - list of cells
    # Vector3f - pos
    SetCommandCells = 18

    # CmdId - command id
    # EntId - unit
    RemoveCommandFromQueue = 19

    # string -- the debug command string
    # Vector3f -- mouse pos (in world coords)
    # uint8 -- focus army index
    # EntIdSet -- selection
    DebugCommand = 20

    # string -- the lua string to evaluate in the sim state
    ExecuteLuaInSim = 21

    # string - callback function name
    # LuaObject - table of function arguments
    LuaSimCallback = 22

    # no args.
    EndGame = 23


# Format of EntIdSet:
#
# uint32 - number of entity ids
# repeat number of entity ids times {
#   EntId - entity id
# }


# Format of CmdData:
#
# CmdId - id
# uint8 - command type (EUnitCommandType)
# STITarget - target
# int32 - formation index or -1
# if formation index != -1
# {
#   Quaternionf - formation orientation
#   float - formation scale
# }
# string - blueprint ID or the empty string for no blueprint
# ListOfCells - cells
# int32 - count


# Format of STITarget:
#
# uint8 - target type (ESTITargetType)
# if target type == STITARGET_Entity {
#   EntId - entity id
# }
# if target type == STITARGET_Position {
#   Vector3f - position
# }


# Format of ListOfCells:
#
# uint32 - num cells
# repeat num cells times {
#   int16 - x
#   int16 - z
# }


CommandStateNames = [
    "Advance",
    "SetCommandSource",
    "CommandSourceTerminated",
    "VerifyChecksum",
    "RequestPause",
    "Resume",
    "SingleStep",
    "CreateUnit",
    "CreateProp",
    "DestroyEntity",
    "WarpEntity",
    "ProcessInfoPair",
    "IssueCommand",
    "IssueFactoryCommand",
    "IncreaseCommandCount",
    "DecreaseCommandCount",
    "SetCommandTarget",
    "SetCommandType",
    "SetCommandCells",
    "RemoveCommandFromQueue",
    "DebugCommand",
    "ExecuteLuaInSim",
    "LuaSimCallback",
    "EndGame",
]


class ActionType:
    NONE = 0
    Stop = 1
    Move = 2
    Dive = 3
    FormMove = 4
    BuildSiloTactical = 5
    BuildSiloNuke = 6
    BuildFactory = 7
    BuildMobile = 8
    BuildAssist = 9
    Attack = 10
    FormAttack = 11
    Nuke = 12
    Tactical = 13
    Teleport = 14
    Guard = 15
    Patrol = 16
    Ferry = 17
    FormPatrol = 18
    Reclaim = 19
    Repair = 20
    Capture = 21
    TransportLoadUnits = 22
    TransportReverseLoadUnits = 23
    TransportUnloadUnits = 24
    TransportUnloadSpecificUnits = 25
    DetachFromTransport = 26
    Upgrade = 27
    Script = 28
    AssistCommander = 29
    KillSelf = 30
    DestroySelf = 31
    Sacrifice = 32
    Pause = 33
    OverCharge = 34
    AggressiveMove = 35
    FormAggressiveMove = 36
    AssistMove = 37
    SpecialAction = 38
    Dock = 39
