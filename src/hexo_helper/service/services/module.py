import tkinter
from typing import Optional, Type

from src.hexo_helper.common.constants import ModuleRegistryKey
from src.hexo_helper.common.module import (
    Module,
    get_module_registry,
)
from src.hexo_helper.exceptions import (
    ActivateTreeException,
    ModuleInstanceNotFoundException,
)
from src.hexo_helper.service.constants import MODULE_MAIN
from src.hexo_helper.service.enum import ServiceName
from src.hexo_helper.service.services.base import Service


class ModuleService(Service):
    @classmethod
    def get_name(cls):
        return ServiceName.MODULE.value

    def _get_operation_mapping(self) -> dict:
        return {
            "activate": self.activate,
            "deactivate": self.deactivate,
        }

    def shutdown(self):
        # when close is clicked, modules has been cleaned up.
        return

    def __init__(self, root: tkinter.Tk):
        super().__init__()
        self.root = root
        self.activated_tree: Module | None = None

    def start(self):
        """
        Kicks off the application by activating the initial root module(s).
        """
        registry = get_module_registry()
        root_module: str = MODULE_MAIN  # noqa
        root_data = registry.get(root_module)

        self.activated_tree = self._build_activated_tree(root_module, root_data, None)

    def _build_activated_tree(
        self, module_id: str, module_info: dict, parent_instance: Optional[Module]
    ) -> Optional[Module]:
        """
        Recursively builds the initial tree of activated modules using the shared helper.
        """
        activate_immediately: bool = module_info.get(ModuleRegistryKey.ACTIVATE_IMMEDIATELY.value, False)
        if not activate_immediately:
            return None

        instance_name = module_id.split(".")[-1]
        module_instance = self._create_and_prepare_module(module_id, instance_name, parent_instance)

        # Recursively build the tree for children
        children_info = module_info.get(ModuleRegistryKey.CHILD_MODULES.value, {})
        if children_info:
            for child_name, child_info in children_info.items():
                child_id = f"{module_id}.{child_name}"
                # Pass the current module instance as the parent for the next level
                child_module = self._build_activated_tree(child_id, child_info, module_instance)
                if not child_module:
                    continue
                # Add the fully constructed child to the current instance
                module_instance.add_child(child_name, child_module)

        return module_instance

    def get_registered_module_info(self, module_id: str) -> dict:
        """
        Retrieves module metadata directly from the flat registry.
        This is much more efficient than traversing a nested dictionary.
        """
        # We can now directly access the original flat registry for info.
        registry = get_module_registry()
        if module_id not in registry:
            raise KeyError(f"Module with ID '{module_id}' not found in registry.")
        return registry[module_id]

    def get_activated_instance(self, id: str) -> Module | None:
        parts = id.split(".")
        current = self.activated_tree

        if current.get_id() != parts[0]:
            raise ModuleInstanceNotFoundException(
                f"Root module instance mismatch: expected '{current.get_id()}', got '{parts[0]}'"
            )

        for part in parts[1:]:
            if part not in current.children:
                return None
            current = current.children[part]

        return current

    @staticmethod
    def _get_from_dict(d: dict, path: str):
        current = d
        parts = path.split(".")
        for i, part in enumerate(parts):
            if part not in current:
                raise KeyError(f"Module path not found: {'.'.join(parts[:i + 1])}")

            module_info = current[part]

            if i == len(parts) - 1:
                return module_info

            # recursion
            current = module_info.get(ModuleRegistryKey.CHILD_MODULES.value)
            if current is None:
                raise KeyError(f"No child modules under: {'.'.join(parts[:i + 1])}")

    def activate(self, module_id: str, parent_instance_id: Optional[str]):
        """
        Dynamically activates a new module and adds it to the live tree using the shared helper.
        """
        module_info: dict = self.get_registered_module_info(module_id)
        module_cls: Type[Module] = module_info[ModuleRegistryKey.CLASS.value]
        is_unique: bool = module_info[ModuleRegistryKey.IS_UNIQUE.value]
        instance_name = module_id.split(".")[-1]

        # This logic for handling non-unique modules remains only in `activate`
        if not is_unique:
            module_cls.count_increment()
            current_count = module_cls.get_count()
            instance_name += f"@{current_count}"

        if not parent_instance_id:
            # It creates the module but does not attach it to self.activated_tree.
            self._create_and_prepare_module(module_id, instance_name, None)
            return

        instance = self.get_activated_instance(f"{parent_instance_id}.{instance_name}")
        if instance:
            instance.highlight_view()
            return

        # Get the parent instance from the live activated tree
        parent_instance: Module = self.get_activated_instance(parent_instance_id)

        # Use the shared helper to create and prepare the new module instance
        module = self._create_and_prepare_module(module_id, instance_name, parent_instance)

        # Add the new, fully prepared node to the parent in the live tree
        parent_instance.add_child(instance_name, module)

    def deactivate(self, instance_id: str):
        instance: Module = self.get_activated_instance(instance_id)
        # deactivate children
        if instance.children:
            for child in list(instance.children.values()):
                self.deactivate(child.instance_id)

        instance.deactivate()

        id_parts = instance_id.split(".")

        # Case 1: Deactivating the root of the tree.
        if len(id_parts) == 1:
            if not self.activated_tree:
                raise ActivateTreeException

            if not self.activated_tree.instance_id == instance_id:
                raise ModuleInstanceNotFoundException
            self.activated_tree = None
            return

        # Case 2: Deactivating a child module.
        # find its parent to remove it from the parent's `children` dict.
        parent_id = ".".join(id_parts[:-1])
        instance_name = id_parts[-1]

        parent_instance = self.get_activated_instance(parent_id)
        if instance_name not in parent_instance.children:
            raise ModuleInstanceNotFoundException
        # Remove the instance from its parent's tracking.
        del parent_instance.children[instance_name]

    def _create_and_prepare_module(
        self, module_id: str, instance_name: str, parent_instance: Optional[Module]
    ) -> Module:
        # 1. Load registered module info
        module_info: dict = self.get_registered_module_info(module_id)
        module_cls: Type[Module] = module_info[ModuleRegistryKey.CLASS.value]

        # 2. Configure instance based on whether it's a root or child module
        if parent_instance:
            # It's a child module, so it inherits its master from the parent
            instance_id = f"{parent_instance.get_instance_id()}.{instance_name}"
            master = parent_instance.get_master()
        else:
            # It's a root module, so it uses the main Tk instance
            instance_id = instance_name
            master = self.root

        # 3. Create module instance
        module = module_cls(instance_id, master)
        # 4. Set instance properties and call its setup method
        module.on_ready()

        return module
