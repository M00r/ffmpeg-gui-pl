# Ładowanie wtyczek z presetami z katalogu builtin i ~/.ffmpeg_gui_pl/plugins.

import importlib.util
from pathlib import Path

from config import CONFIG_DIR


PLUGINS_USER_DIR = CONFIG_DIR / "plugins"


def _load_file(path: Path) -> dict:
    """Ładuje moduł z pliku i zwraca słownik PRESETS (jeśli istnieje)."""
    try:
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return {}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        presets = getattr(module, "PRESETS", {})
        if isinstance(presets, dict):
            return presets
    except Exception as e:
        print(f"[plugins] Błąd ładowania {path}: {e}")
    return {}


def load_plugin_presets() -> dict:
    """Zwraca słownik wszystkich presetów z wtyczek (builtin + user)."""
    result = {}

    # Wtyczki wbudowane.
    builtin = Path(__file__).parent / "builtin"
    if builtin.exists():
        for p in sorted(builtin.glob("*.py")):
            if p.name.startswith("_"):
                continue
            result.update(_load_file(p))

    # Wtyczki użytkownika.
    PLUGINS_USER_DIR.mkdir(parents=True, exist_ok=True)
    for p in sorted(PLUGINS_USER_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        result.update(_load_file(p))

    return result


def list_plugins() -> list:
    """Zwraca listę ścieżek wtyczek (builtin + user)."""
    out = []
    builtin = Path(__file__).parent / "builtin"
    if builtin.exists():
        out += [p for p in sorted(builtin.glob("*.py")) if not p.name.startswith("_")]
    PLUGINS_USER_DIR.mkdir(parents=True, exist_ok=True)
    out += [p for p in sorted(PLUGINS_USER_DIR.glob("*.py")) if not p.name.startswith("_")]
    return out