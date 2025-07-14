from abc import abstractmethod

from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.client_api import ClientAPI, client_api


class CommunicationController(Controller):
    def __init__(self, model: Model | None, view: View | None):
        super().__init__(model, view)
        self.api: ClientAPI = client_api

    @abstractmethod
    def setup_handlers(self):
        pass

    def set_instance_id(self, instance_id: str):
        self.instance_id = instance_id

    def get_model_key(self) -> list:
        return self.model.keys()

    def get_model_data(self) -> dict:
        return {key: self.api.read_setting(key) for key in self.get_model_key() if key is not None}
