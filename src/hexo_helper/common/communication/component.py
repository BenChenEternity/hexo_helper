from src.hexo_helper.core.event import Consumer, EventBus, Producer

service_request_bus = EventBus()
command_bus = EventBus()


class ServiceConsumer(Consumer):
    def __init__(self):
        super().__init__(service_request_bus)


class ExternalProducer(Producer):
    def __init__(self):
        super().__init__(service_request_bus)


class CommandProducer(Producer):
    def __init__(self):
        super().__init__(command_bus)


class ExternalConsumer(Consumer):
    def __init__(self):
        super().__init__(command_bus)
