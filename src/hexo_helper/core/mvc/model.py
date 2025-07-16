from typing import Any, Dict

from src.hexo_helper.core.utils.compare import deep_equals


class Model:
    def get(self, key: str) -> Any:
        if not hasattr(self, key):
            raise AttributeError(f"{key} doesn't exist in {self.__class__.__name__}")
        return getattr(self, key, None)

    def set(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise AttributeError(f"{key} doesn't exist in {self.__class__.__name__}")
        setattr(self, key, value)

    def init(self, data):
        self.update(data)

    def update(self, data):
        for key, value in data.items():
            self.set(key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def cleanup(self):
        pass

    def keys(self):
        """
        ignore private keys
        """
        return [k for k in self.__dict__.keys() if not k.startswith("_")]


class DiffModel(Model):
    def __init__(self):
        self._origin = {}
        self._dirty_fields = set()

    def get(self, key: str) -> Any:
        # Get directly from the instance's attributes
        if not hasattr(self, key):
            raise AttributeError(f"'{key}' doesn't exist in {self.__class__.__name__}")
        return getattr(self, key)

    def set(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise AttributeError(f"'{key}' doesn't exist in {self.__class__.__name__}")

        current_value = getattr(self, key)

        # If the value remains unchanged, do nothing.
        if deep_equals(current_value, value):
            return

        # Update the current attribute.
        setattr(self, key, value)

        # Check against the original value to determine if it's dirty.
        if key in self._origin and not deep_equals(getattr(self, key), self._origin[key]):
            self._dirty_fields.add(key)
        else:
            # If it's now back to the original value, remove it from dirty fields.
            self._dirty_fields.discard(key)

    def init(self, data):
        for key, value in data.items():
            setattr(self, key, value)
            # set original value
            self._origin[key] = value

    def update(self, data: Dict[str, Any]):
        for key, value in data.items():
            self.set(key, value)

    def to_dict(self) -> Dict[str, Any]:
        # Return a dictionary of current attributes, excluding internal ones
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def is_dirty(self) -> bool:
        return len(self._dirty_fields) > 0

    def get_dirty_fields(self) -> set:
        return self._dirty_fields

    def apply(self):
        if not self._dirty_fields:
            return

        # Apply current changes to _origin and clear dirty fields
        for key in self._dirty_fields:
            self._origin[key] = getattr(self, key)
        self._dirty_fields.clear()

    def cleanup(self):
        # Revert all changes back to the original state
        for key in self._dirty_fields:
            setattr(self, key, self._origin[key])
        self._dirty_fields.clear()
