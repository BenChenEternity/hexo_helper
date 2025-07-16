from src.hexo_helper.common.module import Module, register_module
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.constants import MODULE_MAIN
from src.hexo_helper.service.modules.main.controller import MainController
from src.hexo_helper.service.modules.main.model import MainModel
from src.hexo_helper.service.modules.main.view import MainView


@register_module(MODULE_MAIN)
class MainModule(Module):
    @classmethod
    def get_mvc(cls) -> tuple[type[Model] | None, type[View] | None, type[Controller] | None]:
        return MainModel, MainView, MainController
