import ttkbootstrap as ttkb

from src.hexo_helper.i18n import setup_translations
from src.hexo_helper.service.client_api import client_api
from src.hexo_helper.service.enum import BlackboardKey, ServiceName
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.settings import DEFAULT_SETTINGS, LANGUAGES, THEMES


class ConfigService(Service):

    @classmethod
    def get_name(cls):
        return ServiceName.CONFIG.value

    def __init__(self):
        super().__init__()
        self.style = ttkb.Style()

    def start(self):
        # language
        language = client_api.read_setting(BlackboardKey.LANGUAGE.value)
        if language not in LANGUAGES:
            language = DEFAULT_SETTINGS[BlackboardKey.LANGUAGE.value]
        self.set_language(language)
        # theme
        theme = client_api.read_setting(BlackboardKey.THEME.value)
        if theme not in THEMES:
            theme = DEFAULT_SETTINGS.get(BlackboardKey.THEME.value)
        self.set_theme(theme)

    def _get_operation_mapping(self) -> dict:
        return {
            "set_language": self.set_language,
            "set_theme": self.set_theme,
        }

    def shutdown(self):
        pass

    def set_language(self, language: str):
        setup_translations(language)

    def set_theme(self, theme: str):
        self.style.theme_use(theme)
