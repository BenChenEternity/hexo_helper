import logging
import platform
from collections import OrderedDict
from pathlib import Path

import platformdirs

# --- runtime info ---
os_type = platform.system()

# --- basic ---
APP_NAME = "Hexo Helper"
DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "cosmo",
}

# --- path ---
ROOT_PATH = Path(__file__).parent.parent.parent.resolve()

ASSETS_PATH = ROOT_PATH / "assets"
IMAGE_PATH = ASSETS_PATH / "images"
LOCALE_DIR = ROOT_PATH / "locale"

# --- user data ---
BASE_DATA_DIR = Path(platformdirs.user_data_dir())
APP_DATA_DIR = BASE_DATA_DIR / APP_NAME
SETTINGS_FILE_PATH = APP_DATA_DIR / "settings.json"

# --- i18n ---
DOMAINS = ["_", "modules", "services"]
# 设置中可选的语言
LANGUAGES = OrderedDict(
    {
        "en": "English",
        "zh-cn": "简体中文",
        "zh-tw": "繁體中文",
    }
)

# --- themes ---
THEMES = OrderedDict(
    {
        # --- ttkbootstrap light themes ---
        "litera": "Litera (Modern Flat)",
        "cosmo": "Cosmo (Modern Bootswatch)",
        "flatly": "Flatly (Modern Flat)",
        "journal": "Journal (Modern Sketchy)",
        "lumen": "Lumen (Modern Bright)",
        "minty": "Minty (Modern Green)",
        "pulse": "Pulse (Modern Vibrant)",
        "sandstone": "Sandstone (Modern Warm)",
        "united": "United (Modern Ubuntu)",
        "yeti": "Yeti (Modern Clean)",
        # --- ttkbootstrap dark themes ---
        "superhero": "Superhero (Dark)",
        "darkly": "Darkly (Dark)",
        "cyborg": "Cyborg (Dark Blue)",
        "vapor": "Vapor (Dark Pink/Purple)",
    }
)

# --- Log ---
LOG_FILE_PATH = APP_DATA_DIR / "app.log"
ROOT_LOGGER_LEVEL = logging.DEBUG
CONSOLE_HANDLER_LEVEL = logging.INFO
FILE_HANDLER_LEVEL = logging.DEBUG

try:
    from local_settings import *  # noqa
except ImportError:
    pass
