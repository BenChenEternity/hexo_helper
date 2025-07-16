import importlib
import pkgutil


def discover_and_import_modules(path, package_name):
    for _, name, is_pkg in pkgutil.walk_packages(path, prefix=package_name + "."):
        importlib.import_module(name)
