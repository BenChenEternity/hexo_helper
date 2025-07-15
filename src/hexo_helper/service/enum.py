from enum import Enum


class BlackboardKey(Enum):
    APP_NAME = "app_name"
    LANGUAGE = "language"
    THEME = "theme"
    COMMAND_OUTPUT = "command_output"
    OPEN_PROJECTS = "open_projects"
    SELECTED_PROJECT = "selected_project"


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
