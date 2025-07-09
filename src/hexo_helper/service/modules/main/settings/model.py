import logging

from src.hexo_helper.core.mvc.model import DiffModel

logger = logging.getLogger(__name__)


class SettingsModel(DiffModel):
    def __init__(self):
        super().__init__()
        self.language = None
        self.theme = None
