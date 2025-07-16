from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.service.client_api import client_api


class BlackboardMixin:
    model: Model

    def get_model_data(self):
        keys = self.model.keys()
        return client_api.read_settings_batch(set(keys))
