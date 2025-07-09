from enum import Enum


class ModuleRegistryKey(Enum):
    NAME = "name"
    CLASS = "class"
    CHILD_MODULES = "child_modules"
    ACTIVATE_IMMEDIATELY = "activate_immediately"
    IS_UNIQUE = "is_unique"
