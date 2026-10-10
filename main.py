# Główne okno aplikacji FFmpeg GUI PL.

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QAction, QFileDialog, QTextEdit, QLabel, QMessageBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QPushButton,
    QStatusBar, QDialog, QTabWidget, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from version import APP_VERSION, APP_NAME
from config import (
    load_config, save_config,
    resolve_ffmpeg, resolve_ffprobe, resolve_ffplay,
    list_profiles, load_profile, save_profile, delete_profile
)
from theme import apply_theme
from ffmpeg_runner import FFmpegWorker, probe_video_info, get_duration
from checksum import compute_directory_checksums
from updater import UpdateChecker
from widgets.progress_bar import ProgressWidget
from widgets.frame_preview import FramePreviewWidget
from widgets.job_queue_widget import JobQueueWidget
from dialogs.convert import ConvertDialog
from dialogs.frame_extract import (
    FrameTypeDialog, IntervalDialog, RangeDialog, SingleFrameDialog
)
from dialogs.debug_vis import DebugVisDialog
from dialogs.batch import BatchDialog
from dialogs.command_editor import CommandEditorDialog
from dialogs.play_dialog import PlayDialog
from dialogs.plugins_dialog import PluginsDialog
from dialogs.update_dialog import UpdateDialog
from settings_dialog import SettingsDialog
from plugins.loader import load_plugin_presets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1280, 820)

        # Wczytaj konfigurację i zastosuj motyw.
        self.cfg = load_config()
        apply_theme(QApplication.instance(), self.cfg.get("theme", "light"))

        # Wykryj narzędzia FFmpeg.
        self.ffmpeg = resolve_ffmpeg(self.cfg)
        self.ffprobe = resolve_ffprobe(self.cfg)
        self.ffplay = resolve_ffplay(self.cfg)

        self.worker = None
        self.update_checker = None
        self.update_info = None
        self._last_output_dir = None
        self._plugin_items = {}

        self._build_menu()
        self._build_ui()
        self._check_ffmpeg()

        # Auto-sprawdzanie aktualizacji po 2 sekundach.
        if self.cfg.get("auto_check_updates", True):
            QTimer.singleShot(2000, lambda: self.check_updates(silent=True))

    # ---------------- MENU ----------------
    def _act(self, text, slot, shortcut=None):
        """Tworzy akcję menu."""
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        return a

    def _build_menu(self):
        mb = self.menuBar()

        m_file = mb.addMenu("Plik")
        m_file.addAction(self._act("Otwórz plik…", self.open_probe, "Ctrl+O"))
        m_file.addAction(self._act("Ustawienia…", self.open_settings, "Ctrl+,"))
        m_file.addSeparator()
        m_file.addAction(self._act("Zakończ", self.close, "Ctrl+Q"))

        m_tools = mb.addMenu("Narzędzia")
        m_tools.addAction(self._act("Edytor poleceń FFmpeg…", self.open_command_editor, "Ctrl+E"))
        m_tools.addAction(self._act("Odtwarzacz FFplay…", self.open_play, "Ctrl+P"))
        m_tools.addAction(self._act("Przetwarzanie wsadowe…", self.open_batch))
        m_tools.addSeparator()
        m_tools.addAction(self._act("Dodaj do kolejki (bieżący log)…", self.add_last_to_queue))
        m_tools.addAction(self._act("Wtyczki i presety…", self.open_plugins))
        m_tools.addSeparator()
        m_tools.addAction(self._act("Oblicz SHA-256 dla katalogu…", self.compute_checksums_dialog))
        m_tools.addAction(self._act("Zweryfikuj checksums.sha256…", self.verify_checksums_dialog))

        m_view = mb.addMenu("Widok")
        m_view.addAction(self._act("Motyw jasny", lambda: self.set_theme("light")))
        m_view.addAction(self._act("Motyw ciemny", lambda: self.set_theme("dark")))

        m_prof = mb.addMenu("Profile")
        m_prof.addAction(self._act("Zapisz bieżące jako profil…", self.save_current_profile))
        m_prof.addAction(self._act("Wczytaj profil…", self.load_profile_dialog))
        m_prof.addAction(self._act("Usuń profil…", self.delete_profile_dialog))

        m_help = mb.addMenu("Pomoc")
        m_help.addAction(self._act("Sprawdź aktualizacje…", lambda: self.check_updates(False)))
        m_help.addSeparator()
        m_help.addAction(self._act("O programie", self.show_about))

    # ---------------- UKŁAD ----------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Pasek informacyjny.
        self.lbl_info = QLabel()
        layout.addWidget(self.lbl_info)
        self._refresh_info()

        # Główny splitter.
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)

        # Drzewko funkcji.
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Funkcje FFmpeg")
        self.tree.setMinimumWidth(400)
        splitter.addWidget(self.tree)

        # Zakładki po prawej.
        self.tabs = QTabWidget()

        # --- Zakładka: log ---
        log_w = QWidget()
        log_l = QVBoxLayout(log_w)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        self.log.setFont(f)
        log_l.addWidget(self.log, 1)

        btn_row = QHBoxLayout()
        self.btn_stop = QPushButton("Zatrzymaj")
        self.btn_stop.clicked.connect(self.stop_worker)
        self.btn_stop.setEnabled(False)
        btn_clear = QPushButton("Wyczyść log")
        btn_clear.clicked.connect(self.log.clear)
        btn_save = QPushButton("Zapisz log…")
        btn_save.clicked.connect(self.save_log)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()
        log_l.addLayout(btn_row)
        self.tabs.addTab(log_w, "Log")

        # --- Zakładka: podgląd klatek ---
        self.preview = FramePreviewWidget()
        self.tabs.addTab(self.preview, "Podgląd klatek")

        # --- Zakładka: kolejka zadań ---
        self.queue = JobQueueWidget()
        self.queue.log_line.connect(self.log.append)
        self.tabs.addTab(self.queue, "Kolejka zadań")

        splitter.addWidget(self.tabs)
        splitter.setSizes([420, 860])

        # Pasek postępu na dole.
        self.progress = ProgressWidget()
        layout.addWidget(self.progress)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Gotowe.")

        self._populate_tree()
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)

    def _refresh_info(self):
        """Odświeża pasek informacyjny ze ścieżkami i wersją."""
        self.lbl_info.setText(
            f"<b>FFmpeg:</b> {self.ffmpeg or '<span style=color:red>brak</span>'} "
            f"&nbsp;|&nbsp; <b>ffprobe:</b> {self.ffprobe or 'brak'} "
            f"&nbsp;|&nbsp; <b>ffplay:</b> {self.ffplay or 'brak'} "
            f"&nbsp;|&nbsp; <b>Wersja:</b> {APP_VERSION} "
            f"&nbsp;|&nbsp; <b>Konfiguracja:</b> ~/.ffmpeg_gui_pl"
        )

    # ---------------- DRZEWKO FUNKCJI ----------------
    def _populate_tree(self):
        t = self.tree
        t.clear()

        # 1. Konwersja.
        conv = QTreeWidgetItem(t, ["1. Konwersja formatów (kontenery)"])
        for fmt, label in [
            ("mp4", "Konwertuj do .mp4"),
            ("avi", "Konwertuj do .avi"),
            ("mov", "Konwertuj do .mov"),
            ("mkv", "Konwertuj do .mkv"),
            ("webm", "Konwertuj do .webm"),
            ("ts", "Konwertuj do .ts"),
            ("flv", "Konwertuj do .flv"),
            ("wmv", "Konwertuj do .wmv"),
            ("gif", "Konwertuj do .gif"),
        ]:
            it = QTreeWidgetItem(conv, [label])
            it.setData(0, Qt.UserRole, ("convert", fmt))
        conv.setExpanded(True)

        # 2. Klatki.
        fr = QTreeWidgetItem(t, ["2. Wyodrębnianie i analiza klatek"])
        by_type = QTreeWidgetItem(fr, ["2.1 Według typu klatki"])
        for ft, label in [
            ("I", "Wyodrębnij wszystkie klatki I (kluczowe)"),
            ("P", "Wyodrębnij wszystkie klatki P"),
            ("B", "Wyodrębnij wszystkie klatki B"),
        ]:
            it = QTreeWidgetItem(by_type, [label])
            it.setData(0, Qt.UserRole, ("frame_type", ft))
        it = QTreeWidgetItem(by_type, ["Wyodrębnij konkretną klatkę (numer/czas)"])
        it.setData(0, Qt.UserRole, ("single_frame", None))

        by_int = QTreeWidgetItem(fr, ["2.2 Według interwału"])
        it = QTreeWidgetItem(by_int, ["Co N-tą klatkę / co N sekund"])
        it.setData(0, Qt.UserRole, ("interval", None))
        it = QTreeWidgetItem(by_int, ["Z zakresu czasu (od–do)"])
        it.setData(0, Qt.UserRole, ("range", None))

        by_dbg = QTreeWidgetItem(fr, ["2.3 Wizualizacja debugowa"])
        it = QTreeWidgetItem(by_dbg, ["Wizualizacja wartości QP (wymaga FFmpeg nightly)"])
        it.setData(0, Qt.UserRole, ("debug", "qp"))
        by_type.setExpanded(True)

        # 3. Makrobloki i wektory.
        mb = QTreeWidgetItem(t, ["3. Analiza wektorów ruchu"])
        it = QTreeWidgetItem(mb, ["Wektory ruchu (codecview)"])
        it.setData(0, Qt.UserRole, ("debug", "mv"))

        # 4. Narzędzia dodatkowe.
        ex = QTreeWidgetItem(t, ["4. Narzędzia dodatkowe"])
        it = QTreeWidgetItem(ex, ["Pokaż informacje o pliku (ffprobe)"])
        it.setData(0, Qt.UserRole, ("probe", None))
        it = QTreeWidgetItem(ex, ["Edytor poleceń FFmpeg…"])
        it.setData(0, Qt.UserRole, ("cmd_editor", None))
        it = QTreeWidgetItem(ex, ["Odtwarzacz FFplay…"])
        it.setData(0, Qt.UserRole, ("play", None))
        it = QTreeWidgetItem(ex, ["Przetwarzanie wsadowe…"])
        it.setData(0, Qt.UserRole, ("batch", None))
        it = QTreeWidgetItem(ex, ["Dodaj operację do kolejki (z logu)…"])
        it.setData(0, Qt.UserRole, ("queue_add", None))

        # 5. Wtyczki i presety.
        plg = QTreeWidgetItem(t, ["5. Wtyczki — własne presety"])
        it = QTreeWidgetItem(plg, ["Zarządzaj wtyczkami…"])
        it.setData(0, Qt.UserRole, ("plugins", None))
        it = QTreeWidgetItem(plg, ["Odśwież listę presetów"])
        it.setData(0, Qt.UserRole, ("plugins_refresh", None))

        # Presety z wtyczek.
        self._plugin_items = {}
        for name, data in load_plugin_presets().items():
            label = data.get("label", name)
            child = QTreeWidgetItem(plg, [f"Uruchom: {label}"])
            child.setData(0, Qt.UserRole, ("plugin_run", name))
            self._plugin_items[name] = data
        plg.setExpanded(True)

    # ---------------- OBSŁUGA KLIKNIĘĆ ----------------
    def on_item_double_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        kind, param = data
        self.run_action(kind, param)

    def run_action(self, kind, param):
        """Wywołuje odpowiednie okno lub akcję w zależności od rodzaju."""
        if kind == "probe":
            self.open_probe()
            return
        if kind == "batch":
            self.open_batch()
            return
        if kind == "cmd_editor":
            self.open_command_editor()
            return
        if kind == "play":
            self.open_play()
            return
        if kind == "queue_add":
            self.add_last_to_queue()
            return
        if kind == "plugins":
            self.open_plugins()
            return
        if kind == "plugins_refresh":
            self._populate_tree()
            return
        if kind == "plugin_run":
            self._run_plugin_preset(param)
            return

        if not self.ffmpeg:
            QMessageBox.critical(self, "Brak FFmpeg",
                                 "Nie znaleziono ffmpeg. Ustaw ścieżkę w Ustawieniach.")
            return

        dlg_map = {
            "convert": lambda: ConvertDialog(self, target_format=param),
            "frame_type": lambda: FrameTypeDialog(self, frame_type=param),
            "interval": lambda: IntervalDialog(self),
            "range": lambda: RangeDialog(self),
            "single_frame": lambda: SingleFrameDialog(self),
            "debug": lambda: DebugVisDialog(self, mode=param),
        }
        dlg = dlg_map.get(kind, lambda: None)()
        if dlg and dlg.exec_() == QDialog.Accepted:
            cmd = dlg.get_command(self.ffmpeg)
            out = getattr(dlg, "output_path", "")
            if out:
                if os.path.isdir(out):
                    self.preview.set_dir(out)
                elif kind in ("frame_type", "interval", "range"):
                    self.preview.set_dir(os.path.dirname(out))
            self.start_ffmpeg(cmd)

    # ---------------- URUCHOMIENIE FFMPEG ----------------
    def start_ffmpeg(self, cmd):
        """Uruchamia pojedyncze polecenie ffmpeg w wątku."""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Zajęte", "Poczekaj na zakończenie.")
            return
        dur = 0.0
        if "-i" in cmd:
            inp = cmd[cmd.index("-i") + 1]
            dur = get_duration(self.ffprobe, inp)

        # Zapamiętaj katalog wyjściowy do generowania sum.
        self._last_output_dir = None
        if cmd:
            last = cmd[-1]
            if os.path.isdir(last):
                self._last_output_dir = last
            elif os.path.isdir(os.path.dirname(last)):
                self._last_output_dir = os.path.dirname(last)

        self.log.append("—" * 60)
        self.progress.reset()
        self.worker = FFmpegWorker(cmd, total_duration=dur)
        self.worker.progress.connect(self.on_progress)
        self.worker.percent.connect(self.progress.set_percent)
        self.worker.finished_ok.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage("Przetwarzanie…")

    def on_progress(self, line):
        self.log.append(line)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def on_finished(self, code):
        self.btn_stop.setEnabled(False)
        if code == 0:
            self.statusBar().showMessage("Zakończono pomyślnie.")
            self.log.append("=== Zakończono (kod 0) ===")
            self.progress.set_percent(100.0)
            self.preview.reload()

            # Automatyczne generowanie sum SHA-256.
            if self.cfg.get("generate_checksums", True) and self._last_output_dir:
                self._generate_checksums(self._last_output_dir)
        else:
            self.statusBar().showMessage(f"Kod {code}.")
            self.log.append(f"=== Zakończono z kodem {code} ===")

    def on_error(self, msg):
        self.btn_stop.setEnabled(False)
        self.log.append("BŁĄD: " + msg)
        self.statusBar().showMessage("Błąd.")

    def stop_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log.append(">>> Zażądano zatrzymania…")

    # ---------------- SHA-256 ----------------
    def _generate_checksums(self, output_dir: str):
        """Generuje plik checksums.sha256 w katalogu wyjściowym."""
        try:
            sums_file = os.path.join(output_dir, "checksums.sha256")
            report = compute_directory_checksums(output_dir, sums_file)
            count = len([l for l in report.splitlines() if l and not l.startswith("#")])
            self.log.append(f"[SHA-256] Zapisano sumy dla {count} plików → {sums_file}")
        except Exception as e:
            self.log.append(f"[SHA-256] Błąd: {e}")

    def compute_checksums_dialog(self):
        """Ręczne obliczenie sum dla wybranego katalogu."""
        d = QFileDialog.getExistingDirectory(self, "Wybierz katalog")
        if not d:
            return
        sums_file = os.path.join(d, "checksums.sha256")
        report = compute_directory_checksums(d, sums_file)
        count = len([l for l in report.splitlines() if l and not l.startswith("#")])
        self.log.append(f"[SHA-256] Wygenerowano sumy dla {count} plików w: {d}")
        self.tabs.setCurrentIndex(0)

    def verify_checksums_dialog(self):
        """Weryfikacja pliku checksums.sha256."""
        from checksum import verify_checksums_file
        p, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik checksums.sha256", "",
            "SHA-256 (*.sha256);;Wszystkie (*)"
        )
        if not p:
            return
        ok, fail, errors = verify_checksums_file(p)
        msg = f"Poprawne: {ok}\nBłędne: {fail}"
        if errors:
            msg += "\n\n" + "\n".join(errors[:20])
        QMessageBox.information(self, "Weryfikacja SHA-256", msg)
        self.log.append(f"[SHA-256] Weryfikacja: OK={ok}, BŁĄD={fail}")

    # ---------------- NARZĘDZIA ----------------
    def open_probe(self):
        """Pokazuje informacje ffprobe o pliku."""
        if not self.ffprobe:
            QMessageBox.warning(self, "Brak ffprobe", "Nie znaleziono ffprobe.")
            return
        p, _ = QFileDialog.getOpenFileName(self, "Wybierz plik do analizy", "", "Wszystkie (*)")
        if not p:
            return
        info = probe_video_info(self.ffprobe, p)
        self.log.append("—" * 60)
        self.log.append(f"ffprobe: {p}")
        self.log.append(info)

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.cfg = load_config()
            apply_theme(QApplication.instance(), self.cfg.get("theme", "light"))
            self.ffmpeg = resolve_ffmpeg(self.cfg)
            self.ffprobe = resolve_ffprobe(self.cfg)
            self.ffplay = resolve_ffplay(self.cfg)
            self._refresh_info()

    def open_batch(self):
        """Otwiera okno przetwarzania wsadowego i dodaje zadania do kolejki."""
        dlg = BatchDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        files, out_dir, op = dlg.get_tasks()
        if not files or not out_dir:
            QMessageBox.warning(self, "Brak danych", "Wybierz pliki i katalog.")
            return
        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            if op.startswith("Konwertuj"):
                ext = op.split(".")[-1]
                out = os.path.join(out_dir, f"{base}.{ext}")
                cmd = [self.ffmpeg, "-y", "-i", f, "-c", "copy", out]
            else:
                ft = op.split()[-1]
                sub = os.path.join(out_dir, base)
                os.makedirs(sub, exist_ok=True)
                pat = os.path.join(sub, f"{base}_{ft}_%05d.png")
                cmd = [self.ffmpeg, "-y", "-i", f,
                       "-vf", f"select='eq(pict_type,{ft})'",
                       "-vsync", "vfr", pat]
            dur = get_duration(self.ffprobe, f)
            self.queue.add_job(f"{base} — {op}", cmd, dur)
        self.tabs.setCurrentWidget(self.queue)

    def open_command_editor(self):
        CommandEditorDialog(self, self.ffmpeg or "ffmpeg",
                            self.ffprobe or "ffprobe").exec_()

    def open_play(self):
        PlayDialog(self, self.ffplay or "ffplay").exec_()

    def open_plugins(self):
        PluginsDialog(self).exec_()
        self._populate_tree()

    def add_last_to_queue(self):
        """Dodaje ostatnie polecenie z logu do kolejki."""
        text = self.log.toPlainText().splitlines()
        last_cmd = None
        for line in reversed(text):
            if line.startswith("$ "):
                last_cmd = line[2:].strip()
                break
        if not last_cmd:
            QMessageBox.information(self, "Brak polecenia",
                                    "W logu nie ma ostatniego polecenia.")
            return
        import shlex
        try:
            parts = shlex.split(last_cmd, posix=False)
        except ValueError:
            parts = last_cmd.split()
        parts = [p.strip('"') for p in parts]
        dur = 0.0
        if "-i" in parts:
            dur = get_duration(self.ffprobe, parts[parts.index("-i") + 1])
        self.queue.add_job(os.path.basename(last_cmd)[:80] or "Zadanie", parts, dur)
        self.tabs.setCurrentWidget(self.queue)
        QMessageBox.information(self, "Dodano", "Polecenie dodane do kolejki.")

    def _run_plugin_preset(self, name: str):
        """Uruchamia preset z wtyczki — pyta o plik i katalog, dodaje do kolejki."""
        if not self.ffmpeg:
            QMessageBox.critical(self, "Brak FFmpeg", "Nie znaleziono ffmpeg.")
            return
        data = self._plugin_items.get(name)
        if not data:
            QMessageBox.warning(self, "Brak presetu", f"Nie znaleziono presetu „{name}”.")
            return

        in_file, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik wejściowy", "", "Wszystkie (*)"
        )
        if not in_file:
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Katalog docelowy")
        if not out_dir:
            return

        ext = data.get("ext", "out")
        base = os.path.splitext(os.path.basename(in_file))[0]
        out_file = os.path.join(out_dir, f"{base}.{ext}")

        # Podstawienie {input} i {output} w poleceniu.
        cmd = [c.format(input=in_file, output=out_file, ffmpeg=self.ffmpeg)
               for c in data.get("cmd", [])]
        if not cmd:
            QMessageBox.warning(self, "Błąd wtyczki", "Preset nie zawiera polecenia.")
            return

        dur = get_duration(self.ffprobe, in_file)
        self.queue.add_job(f"{base} — {data.get('label', name)}", cmd, dur)
        self.tabs.setCurrentWidget(self.queue)
        self.log.append(f">>> Dodano do kolejki: {data.get('label', name)}")

    # ---------------- AKTUALIZACJE ----------------
    def check_updates(self, silent: bool = False):
        """Sprawdza dostępność nowej wersji w tle."""
        if self.update_checker and self.update_checker.isRunning():
            return
        self.statusBar().showMessage("Sprawdzanie aktualizacji…")
        self.update_checker = UpdateChecker()
        self.update_checker.checked.connect(lambda info: self._on_update_checked(info, silent))
        self.update_checker.error.connect(lambda e: self._on_update_error(e, silent))
        self.update_checker.start()

    def _on_update_checked(self, info: dict, silent: bool):
        self.statusBar().showMessage("Gotowe.")
        self.update_info = info
        if info.get("available"):
            dlg = UpdateDialog(self, info)
            dlg.exec_()
        elif not silent:
            QMessageBox.information(self, "Aktualizacje",
                                    "Masz najnowszą wersję programu.")

    def _on_update_error(self, msg: str, silent: bool):
        self.statusBar().showMessage("Gotowe.")
        if not silent:
            QMessageBox.warning(self, "Aktualizacje", msg)

    # ---------------- MOTYW ----------------
    def set_theme(self, name: str):
        """Zmienia motyw i zapisuje w konfiguracji."""
        self.cfg["theme"] = name
        save_config(self.cfg)
        apply_theme(QApplication.instance(), name)

    # ---------------- LOG ----------------
    def save_log(self):
        p, _ = QFileDialog.getSaveFileName(self, "Zapisz log", "", "Text (*.txt);;Wszystkie (*)")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.log.toPlainText())

    # ---------------- PROFILE ----------------
    def save_current_profile(self):
        name, ok = QInputDialog.getText(self, "Profil", "Nazwa profilu:")
        if not ok or not name.strip():
            return
        save_profile(name.strip(), {"config": self.cfg})
        QMessageBox.information(self, "Zapisano", f"Profil „{name}” zapisany.")

    def load_profile_dialog(self):
        names = list_profiles()
        if not names:
            QMessageBox.information(self, "Brak profili", "Nie ma zapisanych profili.")
            return
        name, ok = QInputDialog.getItem(self, "Profil", "Wybierz profil:", names, 0, False)
        if not ok:
            return
        data = load_profile(name)
        if "config" in data:
            self.cfg.update(data["config"])
            save_config(self.cfg)
            apply_theme(QApplication.instance(), self.cfg.get("theme", "light"))
            self.ffmpeg = resolve_ffmpeg(self.cfg)
            self.ffprobe = resolve_ffprobe(self.cfg)
            self.ffplay = resolve_ffplay(self.cfg)
            self._refresh_info()
            QMessageBox.information(self, "Wczytano", f"Profil „{name}” wczytany.")

    def delete_profile_dialog(self):
        names = list_profiles()
        if not names:
            QMessageBox.information(self, "Brak profili", "Nie ma zapisanych profili.")
            return
        name, ok = QInputDialog.getItem(self, "Profil", "Profil do usunięcia:", names, 0, False)
        if not ok:
            return
        delete_profile(name)
        QMessageBox.information(self, "Usunięto", f"Profil „{name}” usunięty.")

    # ---------------- SPRAWDZENIE ----------------
    def _check_ffmpeg(self):
        if not self.ffmpeg:
            QMessageBox.warning(
                self, "Brak FFmpeg",
                "Nie znaleziono <b>ffmpeg</b>.<br>Ustaw ścieżkę w Plik → Ustawienia."
            )

    def show_about(self):
        QMessageBox.information(
            self, "O programie",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "GUI do FFmpeg po polsku:<br>"
            "• konwersja kontenerów z presetami<br>"
            "• wyodrębnianie klatek I/P/B, interwały, zakresy<br>"
            "• wizualizacja makrobloków, QP, wektorów ruchu<br>"
            "• przetwarzanie wsadowe<br>"
            "• kolejka zadań z pauzą/stopem<br>"
            "• edytor poleceń FFmpeg<br>"
            "• odtwarzacz ffplay<br>"
            "• podgląd klatek, profile, motyw jasny/ciemny<br>"
            "• sumy kontrolne SHA-256 dla plików i katalogów<br>"
            "• autoaktualizacja przez GitHub Releases z weryfikacją SHA-256<br>"
            "• wtyczki do własnych presetów"
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()