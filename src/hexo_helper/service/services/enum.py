from enum import Enum


class ServiceName(Enum):
    LOG = "log"
    CONFIG = "config"
    BLACKBOARD = "blackboard"
    RESOURCE = "resource"
    MODULE = "module"
    COMMAND = "command"


class ModuleName(Enum):
    MAIN = "main"
    SETTINGS = "settings"
