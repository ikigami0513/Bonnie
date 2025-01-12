import importlib
from types import ModuleType


def load_settings(settings_path="settings") -> ModuleType:
    try:
        settings = importlib.import_module(settings_path)
        return settings
    except ModuleNotFoundError:
        raise ImportError(f"Impossible de charger le module de settings : {settings_path}")
