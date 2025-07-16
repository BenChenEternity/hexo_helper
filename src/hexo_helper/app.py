import logging

import ttkbootstrap as ttkb

import src.hexo_helper.service.modules  # noqa
from src.hexo_helper.core.log import LoggingManager
from src.hexo_helper.service.services.blackboard import BlackboardService
from src.hexo_helper.service.services.command import CommandService
from src.hexo_helper.service.services.config import ConfigService
from src.hexo_helper.service.services.log import LogService
from src.hexo_helper.service.services.module import ModuleService
from src.hexo_helper.service.services.resource import ResourceService
from src.hexo_helper.services_manager import ServiceManager
from src.hexo_helper.settings import (
    APP_NAME,
    CONSOLE_HANDLER_LEVEL,
    FILE_HANDLER_LEVEL,
    LOG_FILE_PATH,
    ROOT_LOGGER_LEVEL,
)


class Application:
    def __init__(self):
        logging_manager = LoggingManager(
            LOG_FILE_PATH,
            ROOT_LOGGER_LEVEL,
            CONSOLE_HANDLER_LEVEL,
            FILE_HANDLER_LEVEL,
        )
        logging_manager.setup()
        logging.info("Application starting up...")

        # create root window
        self.root = ttkb.Window()
        self.root.withdraw()
        self.root.minsize(800, 600)
        self.root.title(APP_NAME)

        # build services
        blackboard_service = BlackboardService()
        resource_service = ResourceService()
        log_service = LogService(logging_manager)
        config_service = ConfigService()
        module_service = ModuleService(self.root)
        command_service = CommandService()

        # set services
        self.service_manager = ServiceManager()
        # register all services to service manager
        self.service_manager.register(blackboard_service)
        self.service_manager.register(resource_service)
        self.service_manager.register(log_service)
        self.service_manager.register(config_service)
        self.service_manager.register(module_service)
        self.service_manager.register(command_service)

        logging.info("Application UI is ready.")

    def run(self):
        # start services
        self.service_manager.start_up()
        # run main loop
        self.root.mainloop()

        self.service_manager.shutdown()
        logging.info("Application shutting down.")
