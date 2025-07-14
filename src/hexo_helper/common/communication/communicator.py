from typing import Callable

from src.hexo_helper.common.communication.component import (
    ExternalConsumer,
    ExternalProducer,
)


class Communicator:
    """
    communicate with services.
    function: [pack], [send], [receive] event packets
    """

    def __init__(self):
        self.sender = ExternalProducer()
        self.receiver = ExternalConsumer()

    def bind(self, event: str, function: Callable):
        """
        when listening for a specified event, execute corresponding function.
        """
        self.receiver.subscribe(event, function)

    def unbind(self, event: str, function: Callable):
        self.receiver.unsubscribe(event, function)

    def unbind_all(self):
        self.receiver.unsubscribe_all()
