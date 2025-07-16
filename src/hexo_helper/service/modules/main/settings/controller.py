import logging

from src.hexo_helper.common.controller import ServiceRequestController
from src.hexo_helper.service.client_api import client_api
from src.hexo_helper.service.constants import (
    CLOSE_WINDOW_CLICKED,
    COMMAND_REFRESH_I18N,
    MAIN_SETTINGS_APPLY_CLICKED,
    MAIN_SETTINGS_LANGUAGE_SELECTED,
    MAIN_SETTINGS_THEME_SELECTED,
)
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.service.modules.main.settings.model import SettingsModel
from src.hexo_helper.service.modules.main.settings.view import SettingsView

logger = logging.getLogger(__name__)


class SettingsController(ServiceRequestController):
    model: SettingsModel
    view: SettingsView

    def __init__(self, model: SettingsModel, view: SettingsView) -> None:
        super().__init__(model, view)

    def setup_handlers(self):
        self.internal_consumer.subscribe(CLOSE_WINDOW_CLICKED, self._on_close)
        self.internal_consumer.subscribe(MAIN_SETTINGS_LANGUAGE_SELECTED, self._on_language_selected)
        self.internal_consumer.subscribe(MAIN_SETTINGS_THEME_SELECTED, self._on_theme_selected)
        self.internal_consumer.subscribe(MAIN_SETTINGS_APPLY_CLICKED, self._on_apply_clicked)
        self.command_consumer.subscribe(COMMAND_REFRESH_I18N, self._refresh_i18n)

    def on_ready(self):
        super().on_ready()
        self.view.load_images(
            {
                "settings": client_api.load_image("settings.png"),
            }
        )

    def _on_close(self):
        client_api.deactivate_module(self.instance_id)
        self.internal_consumer.unsubscribe_all()
        self.command_consumer.unsubscribe_all()

    def _dirty_check(self):
        if not self.model.is_dirty():
            self.view.clear_dirty()
            return
        self.view.mark_dirty(self.model.get_dirty_fields())

    def _on_language_selected(self, lang_code: str):
        if lang_code == self.model.get(BlackboardKey.LANGUAGE.value):
            # unchanged
            return
        self.model.set(BlackboardKey.LANGUAGE.value, lang_code)
        self._dirty_check()

    def _on_theme_selected(self, theme_code: str):
        if theme_code == self.model.get(BlackboardKey.THEME.value):
            # unchanged
            return
        self.model.set(BlackboardKey.THEME.value, theme_code)
        self._dirty_check()

    def _on_apply_clicked(self):
        dirty_fields = self.model.get_dirty_fields()
        dirty_data = {field: self.model.get(field) for field in dirty_fields}
        client_api.update_settings(dirty_data)

        for k, v in dirty_data.items():
            if k == BlackboardKey.LANGUAGE.value:
                client_api.config_set_language(v)
                client_api.command_refresh_i18n()
                continue

            if k == BlackboardKey.THEME.value:
                client_api.config_set_theme(v)
                continue

        self.model.apply()
        self.view.clear_dirty()

    def _refresh_i18n(self):
        self.view.refresh_i18n()
