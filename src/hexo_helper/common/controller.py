from abc import abstractmethod

from src.hexo_helper.common.component import CommandConsumer
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View


class ServiceRequestController(Controller):
    def __init__(self, model: Model | None, view: View | None):
        super().__init__(model, view)
        self.command_consumer = CommandConsumer()

    @abstractmethod
    def setup_handlers(self):
        pass

    def set_instance_id(self, instance_id: str):
        self.instance_id = instance_id

    def get_model_key(self) -> list:
        return self.model.keys()
