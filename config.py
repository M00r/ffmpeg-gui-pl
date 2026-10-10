# Plik konfiguracji aplikacji — trwałe ustawienia użytkownika.

import os
import json
import shutil
from pathlib import Path

APP_NAME = "FFmpeg GUI PL"
APP_VERSION = "1.0.0"

# Katalog konfiguracji w katalogu domowym użytkownika.
CONFIG_DIR = Path.home() / ".ffmpeg_gui_pl"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_DIR = CONFIG_DIR / "profiles"

# Domyślne ustawienia — używane przy pierwszym uruchomieniu.
DEFAULT_CONFIG = {
    "ffmpeg_path": "",
    "ffprobe_path": "",
    "ffplay_path": "",
    "last_input_dir": "",
    "last_output_dir": "",
    "theme": "light",              # "light" lub "dark"
    "confirm_overwrite": True,
    "keep_log": True,
    "update_channel": "stable",    # "stable" lub "beta"
    "auto_check_updates": True,
    "verify_sha256": True,         # sprawdzaj sumę kontrolną aktualizacji
    "generate_checksums": True,    # generuj sumy po operacji
}


def ensure_dirs():
    """Tworzy katalogi konfiguracji, jeśli nie istnieją."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Wczytuje konfigurację z pliku, uzupełniając brakujące pola domyślnymi."""
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    """Zapisuje konfigurację do pliku JSON."""
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def resolve_ffmpeg(cfg: dict) -> str:
    """Zwraca ścieżkę do ffmpeg — z konfiguracji lub PATH."""
    p = cfg.get("ffmpeg_path", "").strip()
    if p and os.path.isfile(p):
        return p
    return shutil.which("ffmpeg")


def resolve_ffprobe(cfg: dict) -> str:
    """Zwraca ścieżkę do ffprobe."""
    p = cfg.get("ffprobe_path", "").strip()
    if p and os.path.isfile(p):
        return p
    return shutil.which("ffprobe")


def resolve_ffplay(cfg: dict) -> str:
    """Zwraca ścieżkę do ffplay — szuka też obok ffmpeg."""
    p = cfg.get("ffplay_path", "").strip()
    if p and os.path.isfile(p):
        return p
    ff = resolve_ffmpeg(cfg)
    if ff:
        d = os.path.dirname(ff)
        cand = os.path.join(d, "ffplay.exe" if os.name == "nt" else "ffplay")
        if os.path.isfile(cand):
            return cand
    return shutil.which("ffplay")


def list_profiles() -> list:
    """Lista nazw zapisanych profili."""
    ensure_dirs()
    return sorted(f.stem for f in PROFILES_DIR.glob("*.json"))


def load_profile(name: str) -> dict:
    """Wczytuje profil o danej nazwie."""
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(name: str, data: dict):
    """Zapisuje profil do pliku JSON."""
    ensure_dirs()
    with open(PROFILES_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def delete_profile(name: str):
    """Usuwa profil o danej nazwie."""
    p = PROFILES_DIR / f"{name}.json"
    if p.exists():
        p.unlink()