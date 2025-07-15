from src.hexo_helper.common.module import Module
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.modules.main.settings.controller import SettingsController
from src.hexo_helper.service.modules.main.settings.model import SettingsModel
from src.hexo_helper.service.modules.main.settings.view import SettingsView


class SettingsModule(Module):
    @classmethod
    def get_mvc(cls) -> tuple[type[Model] | None, type[View] | None, type[Controller] | None]:
        return SettingsModel, SettingsView, SettingsController
