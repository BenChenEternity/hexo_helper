from collections import defaultdict
from typing import Any, Callable, List, Tuple


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def register(self, event_name: str, callback: Callable[..., Any]):
        """Register an event handler for a consumer."""
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)

    def unregister(self, event_name: str, callback: Callable[..., Any]):
        """Unregister an event handler."""
        # Use a try-except block to avoid an error if the callback does not exist.
        try:
            self._subscribers[event_name].remove(callback)
        except ValueError:
            # Optionally, log a warning here that an attempt was made
            # to unregister a non-existent callback.
            pass

    def emit(self, event_name: str, *args, **kwargs):
        """Producer triggers an event."""
        # Iterate over a copy of the list to allow unsubscribing within a callback.
        results = []
        for callback in self._subscribers.get(event_name, []):
            result = callback(*args, **kwargs)
            if result is not None:
                # if this service do not respond anything, just skip
                results.append(result)
        return results


class Producer:
    def __init__(self, bus: EventBus):
        self.bus = bus

    def send_event(self, event_name: str, *args, **kwargs):
        return self.bus.emit(event_name, *args, **kwargs)


class Consumer:
    """
    Base class for an event consumer.
    Optimization: Automatically tracks subscriptions and provides a method
    to unsubscribe from all at once.
    """

    def __init__(self, bus: EventBus):
        self.bus = bus
        self._subscriptions: List[Tuple[str, Callable]] = []

    def subscribe(self, event_name: str, handler: Callable[..., Any]):
        """Subscribe to an event and record the subscription."""
        self.bus.register(event_name, handler)
        self._subscriptions.append((event_name, handler))

    def unsubscribe(self, event_name: str, handler: Callable[..., Any]):
        """Unsubscribe from a single event and remove it from the records."""
        self.bus.unregister(event_name, handler)
        try:
            self._subscriptions.remove((event_name, handler))
        except ValueError:
            pass

    def unsubscribe_all(self):
        """
        Unsubscribes this consumer instance from all its subscriptions.
        Call this method when the component is destroyed to prevent memory leaks.
        """
        for event_name, handler in self._subscriptions:
            self.bus.unregister(event_name, handler)
        self._subscriptions.clear()
