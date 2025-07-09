from typing import Any

from src.hexo_helper.common.communication.communicator import Communicator
from src.hexo_helper.service.constants import EVENT_REQUEST_SERVICE
from src.hexo_helper.service.services.enum import ServiceName


class ServiceCommunicator(Communicator):
    def _send(self, service: str, operation: str, args: dict):
        context = {
            "name": service,
            "action": {
                "operation": operation,
                "args": args,
            },
        }
        return self.sender.send_event(EVENT_REQUEST_SERVICE, **context)

    def destroy(self):
        self.receiver.unsubscribe_all()

    @staticmethod
    def filter(responses: list, service_name: str):
        return [v for d in responses for k, v in d.items() if k == service_name]

    @staticmethod
    def unique(data_list: list):
        return data_list[0] if data_list else None

    # --- BlackboardService ---
    """
    {
        "name": "blackboard",
        "actions": {
                "operation": "read",
                "args": {"key": ""},
        },
        # {
        #     "operation": "write",
        #     "args": {"key": "", "value": ""},
        # },
        # {
        #     "operation": "update",
        #     "args": {"data": {}},
        # },
    }
    """

    def blackboard_read(self, key: str) -> Any:
        return self.unique(
            self.filter(self._send(ServiceName.BLACKBOARD.value, "read", {"key": key}), ServiceName.BLACKBOARD.value)
        )

    def blackboard_write(self, key: str, value: Any) -> None:
        self._send(ServiceName.BLACKBOARD.value, "write", {"key": key, "value": value})

    def blackboard_update(self, data: dict) -> None:
        self._send(ServiceName.BLACKBOARD.value, "update", {"data": data})

    # --- ModuleService ---
    """
    {
        "name": "module",
        "actions": {
            "operation": "activate",
            "args": {"module_id": "xx", "parent_instance_id": "xx", "model_data": {xx}},
        },
        # {
        #     "operation": "deactivate",
        #     "args": {"instance_id": "xx"},
        # },
    }
    """

    def module_activate(self, module_id: str, parent_instance_id: str) -> None:
        self._send(
            ServiceName.MODULE.value,
            "activate",
            {
                "module_id": module_id,
                "parent_instance_id": parent_instance_id,
            },
        )

    def module_deactivate(self, instance_id: str) -> None:
        self._send(
            ServiceName.MODULE.value,
            "deactivate",
            {
                "instance_id": instance_id,
            },
        )

    # --- ResourceService ---
    """
    {
        "name": "resource",
        "actions": {
            "operation": "load_image",
            "args": {"name": "xx"},
        },
    }
    """

    def resource_load_image(self, name: str):
        return self.unique(
            self.filter(
                self._send(ServiceName.RESOURCE.value, "load_image", {"name": name}),
                ServiceName.RESOURCE.value,
            )
        )

    # --- ConfigService ---
    """
    {
        "name": "config",
        "actions": {
            "operation": "set_language",
            "args": {"language": "xx"},
        },
    }
    """

    def config_set_language(self, lang_code):
        self._send(ServiceName.CONFIG.value, "set_language", {"language": lang_code})

    # --- CommandService ---
    """
    {
        "name": "command",
        "actions": {
            "operation": "refresh_i18n",
        },
    }
    """

    def command_refresh_i18n(self):
        self._send(ServiceName.COMMAND.value, "refresh_i18n", {})


"""
# template
{
    "name": "n",
    "actions": {
        "operation": "a1",
        "args": {"arg1": "v1", "arg2": "v2", ...},
    },
}
"""
