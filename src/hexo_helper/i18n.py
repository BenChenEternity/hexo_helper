import gettext

from .settings import DOMAINS, LOCALE_DIR

_translators = {}


def setup_translations(language: str):
    """
    加载所有域的翻译文件，并存储在模块级的字典中。
    这个函数应该在程序启动和语言切换时被调用。
    """
    global _translators
    _translators = {}

    for domain in DOMAINS:
        try:
            # 为每个域创建一个独立的翻译器对象
            translator = gettext.translation(
                domain=domain,
                localedir=LOCALE_DIR,
                languages=[language],
            )
            # 存储该翻译器的 gettext 方法
            _translators[domain] = translator.gettext
        except FileNotFoundError:
            # 如果某个域的翻译文件不存在，我们存储一个“空”翻译函数
            _translators[domain] = lambda msg: msg


class _Translator:
    """
    一个可调用的类，用于在运行时动态地获取正确的翻译函数。
    这避免了在模块加载时静态绑定一个固定的翻译函数。
    """

    def __init__(self, domain: str):
        self.domain = domain

    def __call__(self, msg: str) -> str:
        """使得类的实例可以像函数一样被调用，例如 _("text")。"""
        # 每次调用时，都从全局字典中动态查找最新的翻译函数
        translator_func = _translators.get(self.domain, lambda m: m)
        return translator_func(msg)


def get_translator(domain: str) -> callable:
    """
    获取一个特定域的、可动态更新的翻译器实例。
    """
    return _Translator(domain)
