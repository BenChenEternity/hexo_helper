from abc import abstractmethod

from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.communicator import ServiceCommunicator


class CommunicationController(Controller):
    def __init__(self, model: Model | None, view: View | None):
        super().__init__(model, view)
        self.communicator: ServiceCommunicator = ServiceCommunicator()

    @abstractmethod
    def setup_handlers(self):
        pass

    def set_instance_id(self, instance_id: str):
        self.instance_id = instance_id

    def get_model_key(self) -> list:
        return self.model.keys()

    def get_model_data(self) -> dict:
        return {key: self.communicator.blackboard_read(key) for key in self.get_model_key() if key is not None}
