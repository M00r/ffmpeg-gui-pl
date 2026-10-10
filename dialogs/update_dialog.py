# Okno aktualizacji — informuje o nowej wersji, pobiera i weryfikuje SHA-256.

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QMessageBox
)

from updater import UpdateDownloader, apply_update
from version import APP_VERSION


class UpdateDialog(QDialog):
    def __init__(self, parent=None, info: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Aktualizacja")
        self.setMinimumWidth(560)
        self.info = info or {}
        self.downloader = None

        layout = QVBoxLayout(self)
        ver = self.info.get("version", "?")
        layout.addWidget(QLabel(
            f"<b>Dostępna nowa wersja: {ver}</b><br>"
            f"Twoja wersja: {APP_VERSION}"
        ))

        # Oczekiwana suma SHA-256 (jeśli dostępna).
        expected = self.info.get("expected_sha256", "")
        if expected:
            layout.addWidget(QLabel(f"<b>Oczekiwana suma SHA-256:</b><br><code>{expected}</code>"))

        layout.addWidget(QLabel("Informacje o wydaniu:"))
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setPlainText(self.info.get("notes", "") or "(brak opisu)")
        layout.addWidget(self.notes, 1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        row = QHBoxLayout()
        self.btn_download = QPushButton("Pobierz i zainstaluj")
        self.btn_download.clicked.connect(self.download)
        self.btn_open = QPushButton("Otwórz stronę wydania")
        self.btn_open.clicked.connect(self.open_page)
        btn_close = QPushButton("Później")
        btn_close.clicked.connect(self.reject)
        row.addWidget(self.btn_download)
        row.addWidget(self.btn_open)
        row.addStretch()
        row.addWidget(btn_close)
        layout.addLayout(row)

    def open_page(self):
        """Otwiera stronę wydania w przeglądarce."""
        url = self.info.get("html_url", "")
        if url:
            from PyQt5.QtGui import QDesktopServices
            from PyQt5.QtCore import QUrl
            QDesktopServices.openUrl(QUrl(url))

    def download(self):
        """Rozpoczyna pobieranie aktualizacji."""
        url = self.info.get("url", "")
        if not url:
            QMessageBox.warning(self, "Brak pliku", "Wydanie nie zawiera pliku do pobrania.")
            return
        self.btn_download.setEnabled(False)
        expected = self.info.get("expected_sha256", "")
        self.downloader = UpdateDownloader(url, expected_sha256=expected)
        self.downloader.progress.connect(self._on_progress)
        self.downloader.finished_ok.connect(self._on_done)
        self.downloader.verify_failed.connect(self._on_verify_failed)
        self.downloader.error.connect(self._on_error)
        self.downloader.start()

    def _on_progress(self, done, total):
        if total <= 0:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(int(done / total * 100))

    def _on_verify_failed(self, msg):
        """Weryfikacja SHA-256 nie powiodła się — nie instalujemy."""
        QMessageBox.critical(self, "Weryfikacja niepowiodła się", msg)
        self.progress.setValue(0)
        self.btn_download.setEnabled(True)

    def _on_done(self, path):
        """Pobrano i zweryfikowano plik — pytamy o instalację."""
        self.progress.setValue(100)
        reply = QMessageBox.question(
            self, "Pobrano i zweryfikowano",
            f"Pobrano plik:\n{path}\n\n"
            "Suma SHA-256 została zweryfikowana pomyślnie.\n\n"
            "Zainstalować teraz?\n"
            "Aplikacja zostanie zamknięta i uruchomiona ponownie.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok = apply_update(path)
            if ok:
                QMessageBox.information(
                    self, "Aktualizacja",
                    "Zaktualizowano. Aplikacja zostanie uruchomiona ponownie."
                )
                from PyQt5.QtWidgets import QApplication
                QApplication.quit()
            else:
                QMessageBox.warning(
                    self, "Błąd",
                    "Nie udało się automatycznie podmienić pliku. "
                    "Otwórz pobrany plik ręcznie i zainstaluj."
                )
        self.btn_download.setEnabled(True)

    def _on_error(self, msg):
        QMessageBox.critical(self, "Błąd", msg)
        self.btn_download.setEnabled(True)