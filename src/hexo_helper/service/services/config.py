from src.hexo_helper.i18n import setup_translations
from src.hexo_helper.service.client_api import client_api
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.service.services.enum import ServiceName


class ConfigService(Service):

    @classmethod
    def get_name(cls):
        return ServiceName.CONFIG.value

    def __init__(self):
        super().__init__()

    def start(self):
        language = client_api.read_setting(BlackboardKey.LANGUAGE.value)
        self.set_language(language)

    def _get_operation_mapping(self) -> dict:
        return {
            "set_language": self.set_language,
        }

    def shutdown(self):
        pass

    def set_language(self, language: str):
        setup_translations(language)
