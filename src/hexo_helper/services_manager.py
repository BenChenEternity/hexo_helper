from typing import Dict

from src.hexo_helper.common.communication.component import ServiceConsumer
from src.hexo_helper.exceptions import ServiceNotFoundException
from src.hexo_helper.service.constants import EVENT_REQUEST_SERVICE
from src.hexo_helper.service.services.base import Service


class ServiceManager:
    def __init__(self):
        self.services: Dict[str:Service] = {}
        self.consumer = ServiceConsumer()
        self._setup_handlers()

    def _setup_handlers(self):
        self.consumer.subscribe(EVENT_REQUEST_SERVICE, self._on_service_requested)

    def register(self, service):
        self.services[service.name] = service

    def _on_service_requested(self, name: str, action: dict):
        service: Service | None = self.services.get(name, None)
        if not service:
            raise ServiceNotFoundException
        if not action:
            return
        return {name: service.exec(action)}

    def shutdown(self):
        """
        shutdown the services
        """
        for service in self.services.values():
            service.shutdown()

    def start_up(self):
        for service in self.services.values():
            service.start()
