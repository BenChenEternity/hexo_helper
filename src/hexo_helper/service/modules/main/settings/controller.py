import logging

from src.hexo_helper.service.constants import (
    CLOSE_WINDOW_CLICKED,
    COMMAND_REFRESH_I18N,
    MAIN_SETTINGS_APPLY_CLICKED,
    MAIN_SETTINGS_LANGUAGE_SELECTED,
)
from src.hexo_helper.service.controller import CommunicationController
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.service.modules.main.settings.model import SettingsModel
from src.hexo_helper.service.modules.main.settings.view import SettingsView

logger = logging.getLogger(__name__)


class SettingsController(CommunicationController):
    model: SettingsModel
    view: SettingsView

    def __init__(self, model: SettingsModel, view: SettingsView) -> None:
        super().__init__(model, view)

    def setup_handlers(self):
        self.internal_consumer.subscribe(CLOSE_WINDOW_CLICKED, self._on_close)
        self.internal_consumer.subscribe(MAIN_SETTINGS_LANGUAGE_SELECTED, self._on_language_selected)
        self.internal_consumer.subscribe(MAIN_SETTINGS_APPLY_CLICKED, self._on_apply_clicked)
        self.api.bind(COMMAND_REFRESH_I18N, self._refresh_i18n)

    def _on_close(self):
        self.api.deactivate_module(self.instance_id)
        self.internal_consumer.unsubscribe_all()
        self.api.unbind_all()

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

    def _on_apply_clicked(self):
        dirty_fields = self.model.get_dirty_fields()
        dirty_data = {field: self.model.get(field) for field in dirty_fields}
        self.api.update_settings(dirty_data)

        for k, v in dirty_data.items():
            if k == BlackboardKey.LANGUAGE.value:
                self.api.config_set_language(v)
                self.api.command_refresh_i18n()
                continue

        self.model.apply()
        self.view.clear_dirty()

    def _refresh_i18n(self):
        self.view.refresh_i18n()
