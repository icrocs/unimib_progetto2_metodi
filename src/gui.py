import sys

from io import BytesIO
from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QFileDialog, QFormLayout, QLineEdit, QPushButton
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from PIL import Image, ImageQt
import jpeg


# Replace or import your black-box processing function here.
# Signature: (path: str, field1: int, field2: int) -> bytes (PNG bytes)
def process_bitmap(path: str, F: int, d: int):
    try:
        img = Image.open(path).convert("L")
    except Exception as exc:
        parser.error(f"Cannot open image: {exc}")

    compressed = jpeg.compress_image(img, F, d)
    buf = BytesIO()
    compressed.save(buf, format="BMP")

    return buf.getvalue()


class ProcessorThread(QThread):
    finished_bytes = pyqtSignal(bytes)
    error = pyqtSignal(str)

    def __init__(self, path: str, F: int, f: int):
        super().__init__()
        self.path = path
        self.F = F
        self.d = f

    def run(self):
        try:
            out = process_bitmap(self.path, self.F, self.d)
            self.finished_bytes.emit(out)
        except Exception as e:
            self.error.emit(str(e))


class BitmapEditorApp(QWidget):
    def __init__(self, img_path, F, d):
        super().__init__()
        self.setWindowTitle("Bitmap Editor (PyQt6)")
        self.orig_pix: Optional[QPixmap] = None
        self.edited_pix: Optional[QPixmap] = None
        self.worker: Optional[ProcessorThread] = None
        
        self.img_path = img_path
        self.F = F
        self.d = d
        
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(self.img_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_btn)
        self.path_edit.returnPressed.connect(self._on_path_entered)


        # Two integer text fields (plain QLineEdit). Defaults "0".
        self.field1_edit = QLineEdit(f"{self.F}")
        self.field2_edit = QLineEdit(f"{self.d}")
        self.field1_edit.setPlaceholderText("integer (e.g. 0)")
        self.field2_edit.setPlaceholderText("integer (e.g. 0)")

        form_layout.addRow("File:", path_row)
        form_layout.addRow("F:", self.field1_edit)
        form_layout.addRow("d:", self.field2_edit)

        # Process button
        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self.on_process_clicked)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.process_btn)

        imgs_layout = QHBoxLayout()
        self.orig_label = QLabel("Original\nNo image")
        self.orig_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orig_label.setMinimumSize(300, 300)
        self.orig_label.setStyleSheet("border: 1px solid gray;")

        self.edited_label = QLabel("Edited\nNo image")
        self.edited_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edited_label.setMinimumSize(300, 300)
        self.edited_label.setStyleSheet("border: 1px solid gray;")

        imgs_layout.addWidget(self.orig_label)
        imgs_layout.addWidget(self.edited_label)
        main_layout.addLayout(imgs_layout)

        if self.img_path:
            self.path_edit.setText(self.img_path)
            self.load_original(self.img_path)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Bitmap", "", "Bitmap Files (*.bmp);;All Files (*)")
        if path:
            self.path_edit.setText(path)
            self.load_original(path)

    def _on_path_entered(self):
        path = self.path_edit.text().strip()
        if path:
            self.load_original(path)

    def _read_int_field(self, edit: QLineEdit, default: int = 0) -> int:
        t = edit.text().strip()
        if not t:
            return default
        try:
            return int(t)
        except ValueError:
            return default

    def load_original(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            self.orig_label.setText("Failed to load image")
            self.orig_pix = None
        else:
            self.orig_pix = pix
            self._update_label_pixmap(self.orig_label, self.orig_pix)

    def on_process_clicked(self):
        path = self.path_edit.text().strip()
        if not path:
            self.edited_label.setText("No input file")
            return
        self.start_processing(path)

    def start_processing(self, path: str):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        f1 = self._read_int_field(self.field1_edit, 0)
        f2 = self._read_int_field(self.field2_edit, 0)
        self.edited_label.setText("Processing...")
        self.worker = ProcessorThread(path, f1, f2)
        self.worker.finished_bytes.connect(self.on_processed)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_processed(self, out_bytes: bytes):
        pix = QPixmap()
        pix.loadFromData(out_bytes, format="BMP")
        if pix.isNull():
            self.edited_label.setText("Failed to create edited pixmap")
            self.edited_pix = None
        else:
            self.edited_pix = pix
            self._update_label_pixmap(self.edited_label, self.edited_pix)

    def on_error(self, msg: str):
        self.edited_label.setText(f"Processing error:\n{msg}")
        self.edited_pix = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.orig_pix:
            self._update_label_pixmap(self.orig_label, self.orig_pix)
        if self.edited_pix:
            self._update_label_pixmap(self.edited_label, self.edited_pix)

    def _update_label_pixmap(self, label: QLabel, pix: QPixmap):
        if pix is None or pix.isNull():
            return
        target = label.size()
        scaled = pix.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled)


def run_app(img_path: str, F: int, d: int):
    app = QApplication(sys.argv)
    w = BitmapEditorApp(img_path, F, d)
    w.show()
    app.exec()
