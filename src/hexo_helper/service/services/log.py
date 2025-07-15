from src.hexo_helper.core.log import LoggingManager
from src.hexo_helper.service.enum import ServiceName
from src.hexo_helper.service.services.base import Service


class LogService(Service):

    @classmethod
    def get_name(cls):
        return ServiceName.LOG.value

    def __init__(self, logging_manager: LoggingManager):
        super().__init__()
        self.logging_manager = logging_manager

    def start(self):
        pass

    def _get_operation_mapping(self) -> dict:
        return {}

    def shutdown(self):
        pass
