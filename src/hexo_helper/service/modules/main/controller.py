from src.hexo_helper.service.client_api import client_api
from src.hexo_helper.service.constants import (
    MAIN_SETTINGS_CLICKED,
    MODULE_MAIN_SETTINGS,
)
from src.hexo_helper.service.controller import ServiceRequestController
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.service.modules.main.model import MainModel
from src.hexo_helper.service.modules.main.view import MainView
from src.hexo_helper.settings import APP_NAME


class MainController(ServiceRequestController):
    view: MainView

    def __init__(self, model: MainModel, view: MainView):
        super().__init__(model, view)

    def setup_handlers(self):
        # UI event
        self.internal_consumer.subscribe(MAIN_SETTINGS_CLICKED, self._on_settings_click)

    def on_ready(self):
        super().on_ready()
        # load images
        self.view.load_images(
            {
                "settings": client_api.load_image("settings.png"),
                "info": client_api.load_image("info.png"),
                "app": client_api.load_image("app.png"),
            }
        )

    def get_model_data(self):
        return {
            BlackboardKey.APP_NAME.value: APP_NAME,
        }

    def _on_settings_click(self):
        client_api.activate_module(
            MODULE_MAIN_SETTINGS,
            self.instance_id,
        )
