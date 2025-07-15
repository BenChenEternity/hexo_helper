import tkinter
from typing import Dict, Optional, Type

from src.hexo_helper.common.constants import ModuleRegistryKey
from src.hexo_helper.common.module import Module
from src.hexo_helper.common.module import create_module_dict as c
from src.hexo_helper.exceptions import (
    ActivateTreeException,
    ModuleInstanceNotFoundException,
)
from src.hexo_helper.service.modules.main.module import MainModule
from src.hexo_helper.service.modules.main.settings.module import SettingsModule
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.service.services.enum import ModuleName, ServiceName

registered_modules = {
    ModuleName.MAIN.value: c(
        MainModule,
        {
            ModuleName.SETTINGS.value: c(
                SettingsModule,
                None,
                False,
            )
        },
    )
}


class ModuleService(Service):
    @classmethod
    def get_name(cls):
        return ServiceName.MODULE.value

    def start(self):
        # build
        self.activated_tree = self._build_activated_tree(
            ModuleName.MAIN.value,
            self.registered_modules[ModuleName.MAIN.value],
            None,
        )

    def _get_operation_mapping(self) -> dict:
        return {
            "activate": self.activate,
            "deactivate": self.deactivate,
        }

    def shutdown(self):
        self.activated_tree.deactivate()

    def __init__(self, root: tkinter.Tk):
        super().__init__()
        self.registered_modules = registered_modules
        self._inject_ids(self.registered_modules)
        self.root = root
        self.activated_tree: Module | None = None

    def _inject_ids(self, module_dict: Dict[str, dict], parent_path: str = ""):
        # dynamic injection
        for name, meta in module_dict.items():
            module_cls = meta[ModuleRegistryKey.CLASS.value]
            full_path = f"{parent_path}.{name}" if parent_path else name
            module_cls.id = full_path

            # recursively inject
            children = meta.get(ModuleRegistryKey.CHILD_MODULES.value)
            if children:
                self._inject_ids(children, full_path)

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

    def get_registered_module_info(self, id: str) -> dict:
        return ModuleService._get_from_dict(self.registered_modules, id)

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

        # 2. Create module instance
        module = module_cls()

        # 3. Configure instance based on whether it's a root or child module
        if parent_instance:
            # It's a child module, so it inherits its master from the parent
            instance_id = f"{parent_instance.get_instance_id()}.{instance_name}"
            master = parent_instance.view.master
        else:
            # It's a root module, so it uses the main Tk instance
            instance_id = instance_name
            master = self.root

        # 4. Set instance properties and call its setup method
        module.set_instance_id(instance_id)
        module.set_master(master)
        module.on_ready()

        return module
