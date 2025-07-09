import logging

from src.hexo_helper.core.mvc.model import Model

logger = logging.getLogger(__name__)


class MainModel(Model):
    def __init__(self):
        self.app_name = None

    # def add_project(self, path: str):
    #     if path in self.open_projects:
    #         logger.info(f"Project: {path} already opened.")
    #         return
    #     self.open_projects.append(path)
    #     self.send_event(EVENT_MAIN_MODEL_PROJECT_OPENED, path=path)
    #
    # def remove_project(self, path: str):
    #     if path not in self.open_projects:
    #         err_msg_title = _("Error")
    #         err_msg = f"{_('Project:')} {path} {_('not opened but closed.')}"
    #         logger.exception(err_msg)
    #         self.send_event(EVENT_ERROR_OCCURRED, title=err_msg_title, message=err_msg)
    #         return
    #     self.open_projects.remove(path)
    #     self.send_event(EVENT_MAIN_MODEL_PROJECT_CLOSED, path=path)
