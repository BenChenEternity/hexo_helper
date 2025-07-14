from typing import Any

from src.hexo_helper.service.communicator import ServiceCommunicator
from src.hexo_helper.service.services.enum import ServiceName


class ClientAPI(ServiceCommunicator):
    """
    An application-specific API layer that provides convenient, high-level
    methods for common cross-controller operations.

    It inherits from the generic ServiceCommunicator and builds upon its
    universal `call` method.
    """

    # --- Blackboard Shortcuts ---
    def read_setting(self, key: str) -> Any:
        """read a setting from the blackboard."""
        return self.call(
            service_name=ServiceName.BLACKBOARD,
            operation="read",
            unique_response=True,
            key=key,
        )

    def update_settings(self, data: dict) -> None:
        """update multiple settings."""
        self.call(
            service_name=ServiceName.BLACKBOARD,
            operation="update",
            data=data,
        )

    # --- Module Shortcuts ---
    def activate_module(self, module_id: str, parent_instance_id: str) -> None:
        """activate a module."""
        self.call(
            service_name=ServiceName.MODULE,
            operation="activate",
            module_id=module_id,
            parent_instance_id=parent_instance_id,
        )

    def deactivate_module(self, instance_id: str) -> None:
        """deactivate a module instance."""
        self.call(
            service_name=ServiceName.MODULE,
            operation="deactivate",
            instance_id=instance_id,
        )

    # --- Resource Shortcuts ---
    def load_image(self, name: str) -> Any:
        """load an image resource."""
        return self.call(
            service_name=ServiceName.RESOURCE,
            operation="load_image",
            unique_response=True,
            name=name,
        )

    # --- Config Shortcuts ---
    def config_set_language(self, language: str) -> None:
        self.call(
            service_name=ServiceName.CONFIG,
            operation="set_language",
            language=language,
        )

    # --- Command Shortcuts ---
    def command_refresh_i18n(self) -> None:
        self.call(
            service_name=ServiceName.COMMAND,
            operation="refresh_i18n",
        )


client_api = ClientAPI()
