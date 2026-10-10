# Bazowe okno dialogowe — wspólny wybór plików wejściowych i wyjściowych.

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QDialogButtonBox,
    QListWidget, QListWidgetItem, QAbstractItemView
)


class BaseDialog(QDialog):
    def __init__(self, parent=None, title="Operacja", allow_multiple=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(560)
        self.input_files = []
        self.output_path = ""
        self.allow_multiple = allow_multiple
        self._common_layout()

    def _common_layout(self):
        """Tworzy wspólny układ: lista plików wejściowych + przyciski."""
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Pliki wejściowe:"))
        self.list_in = QListWidget()
        self.list_in.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_in.setMaximumHeight(120)
        self.layout.addWidget(self.list_in)

        row = QHBoxLayout()
        btn_add = QPushButton("Dodaj pliki…" if self.allow_multiple else "Wybierz plik…")
        btn_add.clicked.connect(self.choose_input)
        btn_del = QPushButton("Usuń zaznaczone")
        btn_del.clicked.connect(self.remove_selected)
        btn_clear = QPushButton("Wyczyść listę")
        btn_clear.clicked.connect(self.clear_inputs)
        row.addWidget(btn_add)
        row.addWidget(btn_del)
        row.addWidget(btn_clear)
        row.addStretch()
        self.layout.addLayout(row)
        self.build_specific()

    def build_specific(self):
        """Do nadpisania w podklasach — specyficzne opcje."""
        pass

    def choose_input(self):
        """Otwiera okno wyboru plików (jednego lub wielu)."""
        filt = "Wideo (*.mp4 *.mkv *.avi *.mov *.webm *.ts *.flv *.wmv *.m4v);;Wszystkie (*)"
        if self.allow_multiple:
            paths, _ = QFileDialog.getOpenFileNames(self, "Wybierz pliki", "", filt)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", filt)
            paths = [path] if path else []
        for p in paths:
            if p and p not in self.input_files:
                self.input_files.append(p)
                QListWidgetItem(p, self.list_in)

    def remove_selected(self):
        """Usuwa zaznaczone pliki z listy."""
        for item in self.list_in.selectedItems():
            row = self.list_in.row(item)
            self.list_in.takeItem(row)
            if row < len(self.input_files):
                del self.input_files[row]

    def clear_inputs(self):
        """Czyści listę plików wejściowych."""
        self.list_in.clear()
        self.input_files = []

    def add_output_dir_row(self, label="Katalog docelowy:"):
        """Dodaje wiersz wyboru katalogu wyjściowego."""
        row = QHBoxLayout()
        self.edit_out = QLineEdit()
        self.edit_out.setReadOnly(True)
        btn = QPushButton("Wybierz…")
        btn.clicked.connect(self.choose_output_dir)
        row.addWidget(QLabel(label))
        row.addWidget(self.edit_out)
        row.addWidget(btn)
        self.layout.addLayout(row)

    def add_output_file_row(self, label="Plik wyjściowy:", ext_filter="Wszystkie (*)"):
        """Dodaje wiersz wyboru pliku wyjściowego."""
        row = QHBoxLayout()
        self.edit_out = QLineEdit()
        self.edit_out.setReadOnly(True)
        btn = QPushButton("Zapisz jako…")
        btn.clicked.connect(lambda: self.choose_output_file(ext_filter))
        row.addWidget(QLabel(label))
        row.addWidget(self.edit_out)
        row.addWidget(btn)
        self.layout.addLayout(row)

    def choose_output_dir(self):
        """Otwiera okno wyboru katalogu docelowego."""
        d = QFileDialog.getExistingDirectory(self, "Katalog docelowy")
        if d:
            self.output_path = d
            self.edit_out.setText(d)

    def choose_output_file(self, ext_filter):
        """Otwiera okno wyboru pliku docelowego."""
        p, _ = QFileDialog.getSaveFileName(self, "Zapisz jako", "", ext_filter)
        if p:
            self.output_path = p
            self.edit_out.setText(p)

    def add_run_buttons(self):
        """Dodaje przyciski Uruchom / Anuluj."""
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Uruchom")
        btns.button(QDialogButtonBox.Cancel).setText("Anuluj")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        self.layout.addWidget(btns)

    def validate(self):
        """Sprawdza, czy wybrano plik wejściowy i wyjściowy."""
        if not self.input_files:
            QMessageBox.warning(self, "Brak danych", "Wybierz plik wejściowy.")
            return False
        if not self.output_path:
            QMessageBox.warning(self, "Brak danych", "Wybierz ścieżkę wyjściową.")
            return False
        return True

    def accept(self):
        """Zamyka okno tylko po pomyślnej walidacji."""
        if self.validate():
            super().accept()

    def get_command(self, ffmpeg_path: str) -> list:
        """Do nadpisania — zwraca listę argumentów polecenia ffmpeg."""
        raise NotImplementedError