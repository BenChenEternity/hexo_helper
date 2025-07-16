from abc import abstractmethod

from src.hexo_helper.core.event import Consumer, EventBus

from .model import Model
from .view import View


class Controller:

    def __init__(self, model: Model | None, view: View | None):
        super().__init__()
        self.model = model
        self.view = view

        # internal bus
        self.internal_consumer: Consumer | None = None

        self.instance_id: str | None = None

    @abstractmethod
    def setup_handlers(self):
        """
        subscribe events
        e.g: self.internal_consumer.subscribe(BUTTON_CLICKED, self.on_button_click)
        """
        pass

    def on_ready(self):
        self.setup_handlers()
        self.model.init(self.get_model_data())
        self.view.create_widgets()
        self.view.setup_bindings()
        self.view.init_data(self.model.to_dict())

    def get_model_data(self):
        pass

    def cleanup(self):
        self.internal_consumer.unsubscribe_all()

    def set_internal_bus(self, internal_bus: EventBus):
        self.internal_consumer = Consumer(internal_bus)
