from abc import abstractmethod
from typing import Dict, Optional, Type

from src.hexo_helper.common.constants import ModuleRegistryKey
from src.hexo_helper.common.controller import ServiceRequestController
from src.hexo_helper.core.event import EventBus
from src.hexo_helper.core.mvc.controller import Controller
from src.hexo_helper.core.mvc.model import Model
from src.hexo_helper.core.mvc.view import View

# modules will be automatically registered here
_module_registry = {}


def register_module(
    module_id: str,
    activate_immediately: bool = True,
    is_unique: bool = True,
):
    """
    decorator to register a module
    """

    def wrapper(clz: Type["Module"]):
        if module_id in _module_registry:
            raise TypeError(f"Module with id '{module_id}' is already registered.")

        # get parent id
        parent_id = None
        if "." in module_id:
            parent_id = module_id.rsplit(".", 1)[0]

        clz.id = module_id

        _module_registry[module_id] = {
            "class": clz,
            "parent_id": parent_id,
            "activate_immediately": activate_immediately,
            "is_unique": is_unique,
            "children": {},
        }
        return clz

    return wrapper


def get_module_registry():
    return _module_registry


class Module:
    id = None
    count = 0

    def __init__(self, instance_id: str, master):
        # M
        self.model: Model | None = None
        # V
        self.master = master
        self.view: View | None = None
        # C
        self.controller: ServiceRequestController | None = None

        # tree structure
        self.instance_id = instance_id
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

    def get_instance_id(self):
        return self.instance_id

    def get_master(self):
        return self.master

    def _init_mvc(self) -> None:
        """
        initialize MVC
        """
        model_class, view_class, controller_class = self.get_mvc()
        model_class: type[Model]
        view_class: type[View]
        controller_class: type[ServiceRequestController]

        # internal event bus V->C for UI events
        internal_bus = EventBus()

        # init MVC
        if model_class:
            self.model = model_class()

        if view_class:
            self.view = view_class()
            self.view.set_internal_bus(internal_bus)
            self.view.set_master(self.master)

        if controller_class:
            self.controller = controller_class(self.model, self.view)
            self.controller.set_internal_bus(internal_bus)

    def on_ready(self):
        if self.controller:
            self.controller.set_instance_id(self.instance_id)
            self.controller.on_ready()

    def deactivate(self):
        """
        cleanup module
        """
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
