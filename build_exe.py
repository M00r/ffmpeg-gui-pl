# Skrypt pakujący aplikację do .exe (Windows) lub binarki.
# Użycie: python build_exe.py

import os
import sys
import subprocess
from pathlib import Path

APP_NAME = "FFmpegGUI"
ENTRY = "main.py"


def ensure_pyinstaller():
    """Instaluje PyInstaller, jeśli go nie ma."""
    try:
        import PyInstaller  # noqa
    except ImportError:
        print("Instaluję PyInstaller…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def create_spec():
    """Zapisuje plik .spec — ułatwia edycję ustawień budowania."""
    spec = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{ENTRY}'],
    pathex=[],
    binaries=[],
    datas=[('plugins', 'plugins')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
                   'plugins.loader'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
)
"""
    Path("ffmpeg_gui.spec").write_text(spec, encoding="utf-8")
    print("Zapisano ffmpeg_gui.spec")


def build():
    """Buduje plik wykonywalny przez PyInstaller."""
    ensure_pyinstaller()
    here = Path(__file__).parent.resolve()

    hidden = [
        "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
        "plugins.loader",
    ]

    args = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--noconsole",
        "--clean",
        "--noconfirm",
        "--add-data", f"plugins{os.pathsep}plugins",
    ]
    for h in hidden:
        args += ["--hidden-import", h]
    args.append(ENTRY)

    print("Uruchamiam:", " ".join(args))
    subprocess.check_call(args, cwd=here)

    dist = here / "dist"
    if dist.exists():
        print(f"\nGotowe. Wynik w: {dist}")
        for f in dist.iterdir():
            print("  -", f.name)
    else:
        print("Nie znaleziono katalogu dist/. Sprawdź logi PyInstallera.")


def build_installer():
    """Kompiluje instalator przez Inno Setup (tylko Windows)."""
    if os.name != "nt":
        print("Pomijam Inno Setup — to narzędzie dla Windows.")
        return
    iscc_candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    iscc = next((p for p in iscc_candidates if os.path.exists(p)), None)
    if not iscc:
        print("Nie znaleziono Inno Setup — zainstaluj z jrsoftware.org.")
        return
    iss = Path(__file__).parent / "installer" / "ffmpeg_gui.iss"
    if not iss.exists():
        print("Nie znaleziono skryptu installer/ffmpeg_gui.iss.")
        return
    subprocess.check_call([iscc, str(iss)])
    print("Instalator utworzony w dist/")


if __name__ == "__main__":
    create_spec()
    build()
    build_installer()