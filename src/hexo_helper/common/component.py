from typing import Any, List

from src.hexo_helper.common.constants import EVENT_REQUEST_SERVICE
from src.hexo_helper.core.event import Consumer, EventBus, Producer

service_request_bus = EventBus()
command_bus = EventBus()


class ServiceConsumer(Consumer):
    def __init__(self):
        super().__init__(service_request_bus)


class ServiceRequestProducer(Producer):
    def __init__(self):
        super().__init__(service_request_bus)

    def call(
        self,
        service_name: str,
        operation: str,
        unique_response: bool = False,
        **kwargs: Any,
    ) -> Any | List[Any] | None:
        """
        Calls a service with a specific operation and arguments.

        Args:
            service_name: service to call.
            operation (str): The name of the operation to execute.
            unique_response (bool): If True, expects a single result and returns it directly.
                                     Otherwise, returns a list of results.
            **kwargs: The arguments for the operation.

        Returns:
            The result from the service. Can be a single value, a list, or None.
        """
        # The _send method now directly uses the operation and kwargs
        context = {
            "name": service_name,
            "action": {
                "operation": operation,
                "args": kwargs,
            },
        }
        responses = self.send_event(EVENT_REQUEST_SERVICE, **context)

        # Filter the responses to get the data from the specific service
        filtered_data = self._filter_responses(responses, service_name)

        if unique_response:
            return filtered_data[0] if filtered_data else None

        return filtered_data

    @staticmethod
    def _filter_responses(responses: list, service_name_value: str) -> list:
        """Filters responses to get results from a specific service."""
        if not responses:
            return []
        # The response structure is [{service_name: result}]
        return [v for d in responses if d for k, v in d.items() if k == service_name_value]


class CommandProducer(Producer):
    def __init__(self):
        super().__init__(command_bus)


class CommandConsumer(Consumer):
    def __init__(self):
        super().__init__(command_bus)
