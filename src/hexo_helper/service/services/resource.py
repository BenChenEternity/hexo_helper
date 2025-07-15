from src.hexo_helper.core.resource import ImageResourceLoader
from src.hexo_helper.service.enum import ServiceName
from src.hexo_helper.service.services.base import Service
from src.hexo_helper.settings import IMAGE_PATH


class ResourceService(Service):

    @classmethod
    def get_name(cls):
        return ServiceName.RESOURCE.value

    def __init__(self):
        super().__init__()
        self.image_loader: ImageResourceLoader | None = None

    def start(self):
        self.image_loader = ImageResourceLoader(IMAGE_PATH)

    def _get_operation_mapping(self) -> dict:
        return {
            "load_image": self.load_image,
        }

    def shutdown(self):
        self.image_loader.clear_cache()

    def load_image(self, name):
        return self.image_loader.load(name)
