from src.hexo_helper.service.constants import (
    MAIN_SETTINGS_CLICKED,
    MODULE_MAIN_SETTINGS,
)
from src.hexo_helper.service.controller import CommunicationController
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.service.modules.main.model import MainModel
from src.hexo_helper.service.modules.main.view import MainView
from src.hexo_helper.settings import APP_NAME


class MainController(CommunicationController):
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
                "settings": self.communicator.resource_load_image("settings.png"),
                "info": self.communicator.resource_load_image("info.png"),
            }
        )

    def get_model_data(self):
        return {
            BlackboardKey.APP_NAME.value: APP_NAME,
        }

    def _on_settings_click(self):
        self.communicator.module_activate(
            MODULE_MAIN_SETTINGS,
            self.instance_id,
        )

    def cleanup(self):
        self.communicator.destroy()

    #
    # def on_open_project(self):
    #     path = filedialog.askdirectory()
    #     if path:
    #         self.model.add_project(path)
