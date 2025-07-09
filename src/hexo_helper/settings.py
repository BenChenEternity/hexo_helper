import logging
from collections import OrderedDict
from pathlib import Path

import platformdirs

# --- 基本信息 ---
APP_NAME = "Hexo Helper"

# --- 默认配置 ---
DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "default",
}

# --- 路径定义 ---
ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
ASSETS_PATH = ROOT_PATH / "assets"
IMAGE_PATH = ASSETS_PATH / "images"
LOCALE_DIR = ROOT_PATH / "locale"

# --- 用户数据路径 (持久化) ---
# 使用 platformdirs 手动构建，确保路径唯一性
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

# Log
LOG_FILE_PATH = APP_DATA_DIR / "app.log"
ROOT_LOGGER_LEVEL = logging.DEBUG
CONSOLE_HANDLER_LEVEL = logging.INFO
FILE_HANDLER_LEVEL = logging.DEBUG

try:
    from local_settings import *  # noqa
except ImportError:
    pass
