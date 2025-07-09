import logging
from abc import abstractmethod

logger = logging.getLogger(__name__)


class Service:
    def __init__(self):
        self._operation_mapping = self._get_operation_mapping()
        self.name = self.get_name()
        logger.debug(f"Service [{self.name}] initialized")

    @classmethod
    @abstractmethod
    def get_name(cls):
        raise NotImplementedError(f"Service should have name: {cls.__name__}")

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def _get_operation_mapping(self) -> dict:
        pass

    def exec(self, action: dict):
        """
        {
            "operation": "xx",
            "args": {xx},
        }
        """
        args = action.get("args", None) or {}
        return self._operation_mapping[action["operation"]](**args)

    @abstractmethod
    def shutdown(self):
        pass
