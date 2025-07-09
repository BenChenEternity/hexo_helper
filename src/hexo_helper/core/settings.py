import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SettingsManager:
    def __init__(self, path: Path):
        self.settings_path = path

    def load_settings(self) -> Dict[str, Any]:
        if self.settings_path is None or not self.settings_path.exists():
            return {}
        try:
            with open(self.settings_path, encoding="utf-8") as f:
                content = f.read()
                if not content:
                    logger.warning("Settings file is empty. Returning default config.")
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error loading settings: {e}. Returning default config.", exc_info=True)
            return {}

    def save_settings(self, settings: Dict[str, Any]):
        if self.settings_path is None:
            logger.error("Cannot save settings, path is not set.")
            return
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except OSError:
            logger.exception("Error saving settings to file.")

    def update_setting(self, data: dict) -> None:
        current_settings = self.load_settings()
        current_settings.update(data)
        self.save_settings(current_settings)
