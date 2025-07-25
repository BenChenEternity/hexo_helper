from typing import Any, Set

from src.hexo_helper.common.component import ServiceRequestProducer
from src.hexo_helper.service.enum import ServiceName


class ClientAPI(ServiceRequestProducer):
    """
    An application-specific API layer that provides convenient, high-level
    methods for common cross-controller operations.
    """

    # --- Blackboard Shortcuts ---
    def read_setting(self, key: str) -> Any:
        """read a setting from the blackboard."""
        return self.call(
            service_name=ServiceName.BLACKBOARD.value,
            operation="read",
            unique_response=True,
            key=key,
        )

    def read_settings_batch(self, keys: Set) -> dict:
        """read multiple setting from the blackboard."""
        return self.call(
            service_name=ServiceName.BLACKBOARD.value,
            operation="read_batch",
            unique_response=True,
            keys=keys,
        )

    def update_settings(self, data: dict) -> None:
        """update multiple settings."""
        self.call(
            service_name=ServiceName.BLACKBOARD.value,
            operation="update",
            data=data,
        )

    # --- Module Shortcuts ---
    def activate_module(self, module_id: str, parent_instance_id: str) -> None:
        """activate a module."""
        self.call(
            service_name=ServiceName.MODULE.value,
            operation="activate",
            module_id=module_id,
            parent_instance_id=parent_instance_id,
        )

    def deactivate_module(self, instance_id: str) -> None:
        """deactivate a module instance."""
        self.call(
            service_name=ServiceName.MODULE.value,
            operation="deactivate",
            instance_id=instance_id,
        )

    # --- Resource Shortcuts ---
    def load_image(self, name: str) -> Any:
        """load an image resource."""
        return self.call(
            service_name=ServiceName.RESOURCE.value,
            operation="load_image",
            unique_response=True,
            name=name,
        )

    # --- Config Shortcuts ---
    def config_set_language(self, language: str) -> None:
        self.call(
            service_name=ServiceName.CONFIG.value,
            operation="set_language",
            language=language,
        )

    def config_set_theme(self, theme: str) -> None:
        self.call(
            service_name=ServiceName.CONFIG.value,
            operation="set_theme",
            theme=theme,
        )

    # --- Command Shortcuts ---
    def command_refresh_i18n(self) -> None:
        self.call(
            service_name=ServiceName.COMMAND.value,
            operation="refresh_i18n",
        )


client_api = ClientAPI()
