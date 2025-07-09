from src.hexo_helper.common.module.module import Module
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.modules.main.controller import MainController
from src.hexo_helper.service.modules.main.model import MainModel
from src.hexo_helper.service.modules.main.view import MainView


class MainModule(Module):
    @classmethod
    def get_mvc(cls) -> tuple[type[Model] | None, type[View] | None, type[Controller] | None]:
        return MainModel, MainView, MainController
