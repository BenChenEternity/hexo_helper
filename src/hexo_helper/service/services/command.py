from src.hexo_helper.common.communication.component import (
    CommandProducer,
)
from src.hexo_helper.service.constants import COMMAND_REFRESH_I18N
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.service.services.enum import ServiceName


class CommandService(Service):
    @classmethod
    def get_name(cls):
        return ServiceName.COMMAND.value

    def __init__(self):
        super().__init__()
        self.command_producer = None

    def start(self):
        self.command_producer: CommandProducer = CommandProducer()

    def _get_operation_mapping(self) -> dict:
        return {
            "refresh_i18n": self.refresh_i18n,
        }

    def shutdown(self):
        pass

    def refresh_i18n(self):
        self.command_producer.send_event(COMMAND_REFRESH_I18N)
