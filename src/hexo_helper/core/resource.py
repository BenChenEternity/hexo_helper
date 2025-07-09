from abc import abstractmethod
from pathlib import Path

from PIL import Image


class ResourceLoader:
    def __init__(self, resource_path: Path):
        self.path = resource_path
        self._cache = {}

    @abstractmethod
    def load(self, name):
        pass

    def get_from_cache(self, name):
        return self._cache.get(name, None)

    def clear_cache(self):
        self._cache.clear()


class ImageResourceLoader(ResourceLoader):
    def __init__(self, resource_path: Path):
        super().__init__(resource_path)

    def load(self, name):
        img = self.get_from_cache(name)
        if img:
            return img

        path = self.path / name
        with Image.open(path) as img:
            img.load()
            return img
        # if not found raise exception
