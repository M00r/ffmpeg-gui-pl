# Obliczanie sum kontrolnych SHA-256 dla plików i katalogów.

import os
import hashlib
from pathlib import Path


def compute_file_sha256(file_path: str, chunk_size: int = 131072) -> str:
    """Oblicza SHA-256 pojedynczego pliku."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_directory_checksums(dir_path: str, output_file: str = "") -> str:
    """
    Oblicza SHA-256 wszystkich plików w katalogu (rekurencyjnie).
    Zwraca raport w formacie kompatybilnym z `sha256sum -c`.
    Opcjonalnie zapisuje raport do pliku.
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        return ""

    lines = []
    for root, _, files in os.walk(dir_path):
        for name in sorted(files):
            fp = Path(root) / name
            # Pomijamy sam plik z sumami, żeby nie wchodził do siebie.
            if fp.name == "checksums.sha256":
                continue
            rel = fp.relative_to(dir_path)
            try:
                digest = compute_file_sha256(str(fp))
                lines.append(f"{digest}  {rel}")
            except Exception as e:
                lines.append(f"# BŁĄD: {rel} — {e}")

    report = "\n".join(lines) + "\n"

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

    return report


def verify_checksums_file(checksums_path: str) -> tuple:
    """
    Weryfikuje plik checksums.sha256.
    Zwraca (ok_count, fail_count, błędy).
    """
    base = Path(checksums_path).parent
    ok, fail = 0, 0
    errors = []
    with open(checksums_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            expected, rel = parts
            fp = base / rel
            if not fp.exists():
                fail += 1
                errors.append(f"Brak pliku: {rel}")
                continue
            actual = compute_file_sha256(str(fp))
            if actual.lower() == expected.lower():
                ok += 1
            else:
                fail += 1
                errors.append(f"Niezgodność: {rel}")
    return ok, fail, errors