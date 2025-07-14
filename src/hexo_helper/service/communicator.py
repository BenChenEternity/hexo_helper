from typing import Any, List

from src.hexo_helper.common.communication.communicator import Communicator
from src.hexo_helper.service.constants import EVENT_REQUEST_SERVICE
from src.hexo_helper.service.services.enum import ServiceName


class ServiceCommunicator(Communicator):
    """
    A generic communicator for sending requests to services.
    It uses a single `call` method to interact with any service,
    making it flexible and easy to extend.
    """

    def call(
        self,
        service_name: ServiceName,
        operation: str,
        unique_response: bool = False,
        **kwargs: Any,
    ) -> Any | List[Any] | None:
        """
        Calls a service with a specific operation and arguments.

        Args:
            service_name (ServiceName): The enum of the service to call.
            operation (str): The name of the operation to execute.
            unique_response (bool): If True, expects a single result and returns it directly.
                                     Otherwise, returns a list of results.
            **kwargs: The arguments for the operation.

        Returns:
            The result from the service. Can be a single value, a list, or None.
        """
        # The _send method now directly uses the operation and kwargs
        context = {
            "name": service_name.value,
            "action": {
                "operation": operation,
                "args": kwargs,
            },
        }
        responses = self.sender.send_event(EVENT_REQUEST_SERVICE, **context)

        # Filter the responses to get the data from the specific service
        filtered_data = self._filter_responses(responses, service_name.value)

        if unique_response:
            return filtered_data[0] if filtered_data else None

        return filtered_data

    def destroy(self):
        """Unsubscribes from all events."""
        self.receiver.unsubscribe_all()

    @staticmethod
    def _filter_responses(responses: list, service_name_value: str) -> list:
        """Filters responses to get results from a specific service."""
        if not responses:
            return []
        # The response structure is [{service_name: result}]
        return [v for d in responses if d for k, v in d.items() if k == service_name_value]
