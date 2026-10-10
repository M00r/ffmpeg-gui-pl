# Autoaktualizacja przez GitHub Releases z weryfikacją SHA-256.

import os
import sys
import json
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
import hashlib
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from version import APP_VERSION, GITHUB_REPO
from config import load_config


# -------- Funkcje pomocnicze --------

def _parse_version(v: str) -> tuple:
    """Zamienia '1.2.3' na (1, 2, 3). Ignoruje przedrostek 'v' i sufiksy."""
    v = v.strip().lstrip("vV")
    base = v.split("-")[0]
    parts = []
    for p in base.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_newer(remote: str, local: str) -> bool:
    """Sprawdza, czy wersja zdalna jest nowsza od lokalnej."""
    return _parse_version(remote) > _parse_version(local)


def _api_get(url: str, timeout: int = 10) -> dict:
    """Wykonuje GET na GitHub API i zwraca sparsowany JSON."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ffmpeg-gui-pl-updater",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _choose_release(releases: list, channel: str) -> dict:
    """Wybiera wydanie zgodnie z kanałem (stable/beta)."""
    for rel in releases:
        if rel.get("draft"):
            continue
        if channel == "stable" and rel.get("prerelease"):
            continue
        return rel
    return {}


def _pick_asset(release: dict) -> dict:
    """Wybiera plik odpowiedni dla bieżącej platformy."""
    assets = release.get("assets", [])
    if not assets:
        return {}

    system = sys.platform
    if system.startswith("win"):
        patterns = (".exe", ".msi")
    elif system == "darwin":
        patterns = (".dmg", ".pkg", ".zip")
    else:
        patterns = (".AppImage", ".deb", ".tar.gz")

    for a in assets:
        name = a.get("name", "")
        # Pomijamy pliki z sumami przy wyborze instalatora.
        if name.endswith(".sha256"):
            continue
        if any(name.endswith(p) for p in patterns):
            return a
    return assets[0] if assets else {}


def _pick_sha256_asset(release: dict) -> dict:
    """Wybiera plik .sha256 powiązany z wydaniem."""
    for a in release.get("assets", []):
        if a.get("name", "").endswith(".sha256"):
            return a
    return {}


def _extract_expected_hash(text: str) -> str:
    """
    Wyciąga hash z pliku .sha256 lub z treści wydania.
    Obsługuje formaty 'hash  plik' i sam hash.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Format: "<hash>  <nazwa_pliku>"
        parts = line.split()
        if parts and len(parts[0]) == 64:
            return parts[0].lower()
    return ""


# -------- Wątek sprawdzający dostępność aktualizacji --------

class UpdateChecker(QThread):
    """Sprawdza w tle, czy jest nowsza wersja."""
    checked = pyqtSignal(dict)
    error = pyqtSignal(str)

    def run(self):
        try:
            cfg = load_config()
            channel = cfg.get("update_channel", "stable")
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
            releases = _api_get(url)
            if not isinstance(releases, list):
                self.error.emit("Nieprawidłowa odpowiedź z GitHub API.")
                return

            rel = _choose_release(releases, channel)
            if not rel:
                self.checked.emit({"available": False})
                return

            tag = rel.get("tag_name", "")
            if not is_newer(tag, APP_VERSION):
                self.checked.emit({"available": False, "version": tag})
                return

            asset = _pick_asset(rel)
            sha_asset = _pick_sha256_asset(rel)

            expected_hash = ""
            # Jeśli jest załączony plik .sha256 — pobieramy go i wyciągamy hash.
            if sha_asset and sha_asset.get("browser_download_url"):
                try:
                    req = urllib.request.Request(
                        sha_asset["browser_download_url"],
                        headers={"User-Agent": "ffmpeg-gui-pl-updater"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as r:
                        expected_hash = _extract_expected_hash(
                            r.read().decode("utf-8", errors="replace")
                        )
                except Exception:
                    pass

            # Fallback — jeśli hash jest w opisie wydania.
            if not expected_hash:
                expected_hash = _extract_expected_hash(rel.get("body", ""))

            self.checked.emit({
                "available": True,
                "version": tag.lstrip("vV"),
                "name": asset.get("name", ""),
                "url": asset.get("browser_download_url", ""),
                "size": asset.get("size", 0),
                "notes": rel.get("body", ""),
                "html_url": rel.get("html_url", ""),
                "expected_sha256": expected_hash,
            })
        except urllib.error.URLError as e:
            self.error.emit(f"Błąd sieci: {e}")
        except Exception as e:
            self.error.emit(f"Błąd aktualizacji: {e}")


# -------- Wątek pobierający plik aktualizacji --------

def compute_sha256(file_path: str, chunk_size: int = 131072) -> str:
    """Oblicza SHA-256 pliku (używane do weryfikacji aktualizacji)."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


class UpdateDownloader(QThread):
    """Pobiera plik aktualizacji i weryfikuje SHA-256."""
    progress = pyqtSignal(int, int)         # (pobrano, całość)
    finished_ok = pyqtSignal(str)           # ścieżka pobranego pliku
    verify_failed = pyqtSignal(str)         # błąd weryfikacji SHA-256
    error = pyqtSignal(str)

    def __init__(self, url: str, expected_sha256: str = "", target_dir: str = ""):
        super().__init__()
        self.url = url
        self.expected_sha256 = expected_sha256
        self.target_dir = target_dir or tempfile.gettempdir()
        self._stop = False

    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "ffmpeg-gui-pl-updater"
            })
            name = self.url.split("/")[-1] or "update.bin"
            dest = Path(self.target_dir) / name

            with urllib.request.urlopen(req, timeout=30) as r:
                total = int(r.headers.get("Content-Length", 0))
                done = 0
                chunk = 64 * 1024
                with open(dest, "wb") as f:
                    while True:
                        if self._stop:
                            break
                        buf = r.read(chunk)
                        if not buf:
                            break
                        f.write(buf)
                        done += len(buf)
                        self.progress.emit(done, total)

            if self._stop:
                dest.unlink(missing_ok=True)
                return

            # Weryfikacja SHA-256 (jeśli mamy oczekiwaną sumę).
            if self.expected_sha256:
                actual = compute_sha256(str(dest))
                if actual.lower() != self.expected_sha256.lower():
                    self.verify_failed.emit(
                        f"Niepowodzenie weryfikacji SHA-256!\n"
                        f"Oczekiwano: {self.expected_sha256}\n"
                        f"Otrzymano: {actual}"
                    )
                    dest.unlink(missing_ok=True)
                    return

            self.finished_ok.emit(str(dest))
        except Exception as e:
            self.error.emit(f"Błąd pobierania: {e}")

    def stop(self):
        """Zatrzymuje pobieranie."""
        self._stop = True


# -------- Aplikowanie aktualizacji --------

def apply_update(file_path: str) -> bool:
    """
    Podmienia bieżący plik wykonywalny na pobrany.
    Windows: uruchamia plik .bat podmieniający po zamknięciu aplikacji.
    Linux/macOS: kopiuje plik i ustawia uprawnienia.
    """
    current = Path(sys.argv[0]).resolve()
    new_file = Path(file_path).resolve()

    if not new_file.exists():
        return False

    if os.name == "nt":
        return _apply_windows(current, new_file)
    return _apply_unix(current, new_file)


def _apply_windows(current: Path, new_file: Path) -> bool:
    """Podmiana pliku na Windows przez skrypt .bat."""
    if new_file.suffix.lower() in (".msi",):
        subprocess.Popen(["msiexec", "/i", str(new_file)])
        return True

    bat = current.parent / "_update_ffmpeg_gui.bat"
    script = f"""@echo off
timeout /t 2 /nobreak >nul
:loop
tasklist /fi "imagename eq {current.name}" | find /i "{current.name}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto loop
)
copy /y "{new_file}" "{current}"
start "" "{current}"
del "%~f0"
"""
    bat.write_text(script, encoding="utf-8")
    subprocess.Popen(["cmd", "/c", str(bat)], creationflags=0x00000008)
    return True


def _apply_unix(current: Path, new_file: Path) -> bool:
    """Podmiana pliku na Linux/macOS."""
    try:
        if new_file.suffix == ".AppImage":
            os.chmod(new_file, 0o755)
        backup = current.with_suffix(current.suffix + ".bak")
        shutil.copy2(current, backup)
        shutil.copy2(new_file, current)
        if current.suffix != ".AppImage":
            os.chmod(current, 0o755)
        return True
    except Exception:
        return False