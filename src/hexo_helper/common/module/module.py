from abc import abstractmethod
from typing import Dict, Optional, Type

from src.hexo_helper.common.constants import ModuleRegistryKey
from src.hexo_helper.core.event import EventBus
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.service.controller import CommunicationController


class Module:
    id = None
    count = 0

    def __init__(self):
        # MVC
        self.model: Model | None = None
        self.view: View | None = None
        self.controller: CommunicationController | None = None

        # tree structure
        self.instance_id = None
        self.children: Dict[str, Module] = {}

        # assemble
        self._init_mvc()

    @classmethod
    @abstractmethod
    def get_mvc(cls) -> tuple[type[Model] | None, type[View] | None, type[Controller] | None]:
        """
        return: model view controller class
        """
        pass

    @classmethod
    def get_id(cls):
        """
        define module_of_id
        """
        return cls.id

    @classmethod
    def get_count(cls):
        return cls.count

    @classmethod
    def count_increment(cls):
        cls.count += 1

    def set_instance_id(self, instance_id: str):
        self.instance_id = instance_id
        self.controller.set_instance_id(instance_id)

    def get_instance_id(self):
        return self.instance_id

    def set_master(self, master):
        self.view.set_master(master)

    def _init_mvc(self) -> None:
        """
        initialize MVC
        """
        model_class, view_class, controller_class = self.get_mvc()
        model_class: type[Model]
        view_class: type[View]
        controller_class: type[CommunicationController]

        # internal event bus V->C for UI events
        internal_bus = EventBus()

        # init MVC
        self.model = model_class() if model_class else None

        if view_class:
            self.view = view_class()
            self.view.set_internal_bus(internal_bus)

        if controller_class:
            self.controller = controller_class(self.model, self.view)
            self.controller.set_internal_bus(internal_bus)

    def on_ready(self):
        if self.controller:
            self.controller.on_ready()

    def deactivate(self):
        """
        cleanup module
        """
        # recursive submodule
        for child_name, child_module in self.children.items():
            child_module.deactivate()

        # cleanup components
        if self.model is not None:
            self.model.cleanup()

        if self.view is not None:
            self.view.cleanup()

        if self.controller is not None:
            self.controller.cleanup()

    def add_child(self, name: str, child: "Module") -> None:
        if name in self.children:
            raise RuntimeError(f"Module ({name}) already exists")
        self.children[name] = child

    def highlight_view(self):
        if not self.view:
            return
        window = self.view.get_window()
        window.deiconify()
        window.lift()
        window.focus_force()


def create_module_dict(
    clz: Type["Module"],
    child_modules: Optional[Dict[str, dict]] = None,
    activate_immediately: bool = True,
    is_unique: bool = True,
):
    """
    Create module information for activation.

    Args:
        clz (Type["Module"]): Class of the module.
        child_modules (Optional[Dict[str, dict]]): Child modules mapped by name. Defaults to None.
        activate_immediately (bool): Whether to activate immediately.
        is_unique (bool): Whether the module is unique.

    Returns:
        dict: Module metadata dictionary.
    """
    return {
        ModuleRegistryKey.CLASS.value: clz,
        ModuleRegistryKey.CHILD_MODULES.value: child_modules,
        ModuleRegistryKey.ACTIVATE_IMMEDIATELY.value: activate_immediately,
        ModuleRegistryKey.IS_UNIQUE.value: is_unique,
    }
