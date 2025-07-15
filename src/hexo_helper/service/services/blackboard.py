import copy

from src.hexo_helper.core.blackboard import Blackboard
from src.hexo_helper.core.settings import SettingsManager
from src.hexo_helper.service.enum import ServiceName
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.settings import DEFAULT_SETTINGS, SETTINGS_FILE_PATH


class BlackboardService(Service):

    @classmethod
    def get_name(cls):
        return ServiceName.BLACKBOARD.value

    def __init__(self):
        super().__init__()
        self.blackboard = Blackboard()
        self.settings_manager = SettingsManager(SETTINGS_FILE_PATH)

    def start(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        user_settings = self.settings_manager.load_settings()
        settings.update(user_settings)
        self.blackboard.update(settings)

    def _get_operation_mapping(self) -> dict:
        return {
            "read": self.read,
            "write": self.write,
            "update": self.update,
        }

    def shutdown(self):
        self.blackboard.clear()

    def read(self, key: str):
        return self.blackboard.get(key)

    def write(self, key: str, value):
        self.blackboard.set(key, value)
        self.settings_manager.update_setting({key: value})

    def update(self, data: dict):
        self.blackboard.update(data)
        self.settings_manager.update_setting(data)
