# module name
from src.hexo_helper.service.enum import ModuleName

MODULE_MAIN = ModuleName.MAIN.value
MODULE_MAIN_SETTINGS = f"{MODULE_MAIN}.{ModuleName.SETTINGS.value}"
MODULE_MAIN_WORKSPACE = f"{MODULE_MAIN}.{ModuleName.WORKSPACE.value}"

# events
# internal events
CLOSE_WINDOW_CLICKED = "close_window_clicked"
MAIN_SETTINGS_CLICKED = "main_settings_clicked"
MAIN_SETTINGS_LANGUAGE_SELECTED = "main_settings_language_selected"
MAIN_SETTINGS_THEME_SELECTED = "main_settings_theme_selected"
MAIN_SETTINGS_APPLY_CLICKED = "main_settings_apply_clicked"
MAIN_INFO_CLICKED = "main_info_clicked"

# command module events
COMMAND_REFRESH_I18N = "command_refresh_i18n"
