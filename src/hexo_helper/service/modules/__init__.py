from src.hexo_helper.core.utils.modules import discover_and_import_modules

# import child modules, to enable decorator
discover_and_import_modules(__path__, __name__)
