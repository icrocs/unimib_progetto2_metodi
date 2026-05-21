import sys
import os

from io import BytesIO
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QSplashScreen, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QFileDialog, QLineEdit, QPushButton, QStatusBar, QFrame, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

from PIL import Image
import jpeg


# ── Dark palette ─────────────────────────────────────────────────────────────
DARK_STYLE = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}
QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 4px 8px;
    color: #cdd6f4;
}
QLineEdit:focus { border: 1px solid #89b4fa; }

QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px 12px;
    color: #cdd6f4;
}
QPushButton:hover  { background-color: #45475a; border: 1px solid #89b4fa; }
QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }

QPushButton#process_btn {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 5px 18px;
}
QPushButton#process_btn:hover   { background-color: #b4befe; }
QPushButton#process_btn:pressed { background-color: #7287fd; }
QPushButton#process_btn:disabled { background-color: #45475a; color: #6c7086; }

QFrame#header_frame {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}
QFrame#controls_frame {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}
QLabel#img_label {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 8px;
    color: #45475a;
    font-size: 14px;
}
QLabel#panel_cap {
    color: #585b70;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    padding: 1px 4px;
}
QStatusBar {
    background-color: #181825;
    color: #6c7086;
    font-size: 11px;
    border-top: 1px solid #313244;
}
"""


# ── Processing logic (unchanged) ─────────────────────────────────────────────
def process_bitmap(path: str, F: int, d: int):
    try:
        img = Image.open(path).convert("L")
    except Exception as exc:
        raise RuntimeError(f"Failed to open Image: {exc}")  #messo raise runtime perche parser.error non c'era come import
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


# ── Main window ──────────────────────────────────────────────────────────────
class BitmapEditorApp(QWidget):
    def __init__(self, img_path, F, d):
        super().__init__()
        self.setWindowTitle("Bitmap Editor — Metodi del Calcolo Scientifico")
        self.setMinimumSize(800, 580)
        self.orig_pix:   Optional[QPixmap] = None
        self.edited_pix: Optional[QPixmap] = None
        self.worker:     Optional[ProcessorThread] = None
        self.img_path = img_path
        self.F = F
        self.d = d
        self._setup_ui()

    # ── UI construction ───────────────────────────────────────────────────────
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_controls())
        root.addLayout(self._build_images(), stretch=1)   
        root.addWidget(self._build_statusbar())

        if self.img_path:
            self.path_edit.setText(self.img_path)
            self.load_original(self.img_path)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("header_frame")
        frame.setFixedHeight(68)

        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 8, 16, 8)
        row.setSpacing(14)

        # Logo (file opzionale da salvare come bicocca_logo.png in src cosi da avere logo bicocca nel titolo, altrimenti viene messa un emoji tipo cappello laurea)
        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(48, 48)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bicocca_logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(48, 48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
            self.logo_lbl.setPixmap(pix)
        else:
            # Placeholder 
            self.logo_lbl.setText("🎓")
            self.logo_lbl.setStyleSheet("font-size: 32px;")
        row.addWidget(self.logo_lbl)

        # Testo titolo + autori
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_lbl = QLabel("Progetto Metodi del Calcolo Scientifico")
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #cdd6f4;")

        authors_lbl = QLabel("Jacopo Borgato  ·  Nicolas Chines")
        authors_lbl.setStyleSheet("color: #6c7086; font-size: 11px;")

        text_col.addWidget(title_lbl)
        text_col.addWidget(authors_lbl)
        row.addLayout(text_col)
        row.addStretch()

        return frame

    # ── Controls (compact single row) ────────────────────────────────────────
    def _build_controls(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("controls_frame")
        frame.setFixedHeight(46)

        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 6, 14, 6)
        row.setSpacing(8)

        # File path
        file_lbl = QLabel("File:")
        file_lbl.setStyleSheet("color: #6c7086;")
        self.path_edit = QLineEdit(self.img_path)
        self.path_edit.setPlaceholderText("Seleziona un file .bmp…")
        self.path_edit.setMinimumWidth(220)
        self.path_edit.returnPressed.connect(self._on_path_entered)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(72)
        browse_btn.clicked.connect(self.browse_file)

        sep = self._vsep()

        # F and d fields (narrow)
        f_lbl = QLabel("F:")
        f_lbl.setStyleSheet("color: #6c7086;")
        self.field1_edit = QLineEdit(f"{self.F}")
        self.field1_edit.setFixedWidth(60)
        self.field1_edit.setPlaceholderText("0")

        d_lbl = QLabel("d:")
        d_lbl.setStyleSheet("color: #6c7086;")
        self.field2_edit = QLineEdit(f"{self.d}")
        self.field2_edit.setFixedWidth(60)
        self.field2_edit.setPlaceholderText("0")

        sep2 = self._vsep()

        self.process_btn = QPushButton("⚙  Process")
        self.process_btn.setObjectName("process_btn")
        self.process_btn.setFixedWidth(120)
        self.process_btn.clicked.connect(self.on_process_clicked)

        for w in (file_lbl, self.path_edit, browse_btn, sep,
                  f_lbl, self.field1_edit, d_lbl, self.field2_edit,
                  sep2, self.process_btn):
            row.addWidget(w)

        return frame

    def _vsep(self) -> QFrame:
        s = QFrame()
        s.setFrameShape(QFrame.Shape.VLine)
        s.setStyleSheet("color: #313244;")
        s.setFixedHeight(24)
        return s

    # ── Image panels ─────────────────────────────────────────────────────────
    def _build_images(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.orig_label   = self._make_img_label("Originale")
        self.edited_label = self._make_img_label("Processata")

        layout.addWidget(self._wrap_panel("ORIGINALE",  self.orig_label))
        layout.addWidget(self._wrap_panel("PROCESSATA", self.edited_label))
        return layout

    def _make_img_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("img_label")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lbl.setMinimumSize(200, 200)
        return lbl

    def _wrap_panel(self, title: str, img_label: QLabel) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        cap = QLabel(title)
        cap.setObjectName("panel_cap")
        v.addWidget(cap)
        v.addWidget(img_label, stretch=1)
        return w

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self) -> QStatusBar:
        self.status = QStatusBar()
        self.status.showMessage("Pronto")
        return self.status

    # ── Logic  ─────────────────────────────────────────────────────
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Apri Bitmap", "", "Bitmap Files (*.bmp);;All Files (*)")
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
            self.orig_label.setText("Impossibile caricare l'immagine")
            self.orig_pix = None
            self.status.showMessage(f"⚠  Errore: {path}")
        else:
            self.orig_pix = pix
            self._update_label_pixmap(self.orig_label, self.orig_pix)
            self.status.showMessage(f"✓  Caricata: {path}")

    def on_process_clicked(self):
        path = self.path_edit.text().strip()
        if not path:
            self.edited_label.setText("Nessun file selezionato")
            return

        f1 = self._read_int_field(self.field1_edit, 0)
        f2 = self._read_int_field(self.field2_edit, 0)
        param_err = jpeg.validate_params(Image.open(path).convert("L"), f1, f2)
        if param_err:
            self.edited_label.setText(param_err)
            return

        self.start_processing(path)

    def start_processing(self, path: str):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        F = self._read_int_field(self.field1_edit, 0)
        d = self._read_int_field(self.field2_edit, 0)

        
        self.edited_label.setText("Elaborazione in corso…")
        self.process_btn.setEnabled(False)
        self.status.showMessage("⏳  Elaborazione in corso…")
        self.worker = ProcessorThread(path, F, d)
        self.worker.finished_bytes.connect(self.on_processed)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_processed(self, out_bytes: bytes):
        pix = QPixmap()
        pix.loadFromData(out_bytes, format="BMP")
        self.process_btn.setEnabled(True)
        if pix.isNull():
            self.edited_label.setText("Errore nella creazione del pixmap")
            self.edited_pix = None
            self.status.showMessage("⚠  Elaborazione fallita")
        else:
            self.edited_pix = pix
            self._update_label_pixmap(self.edited_label, self.edited_pix)
            self.status.showMessage("✓  Elaborazione completata")

    def on_error(self, msg: str):
        self.edited_label.setText(f"Errore:\n{msg}")
        self.edited_pix = None
        self.process_btn.setEnabled(True)
        self.status.showMessage(f"⚠  {msg}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.orig_pix:
            self._update_label_pixmap(self.orig_label, self.orig_pix)
        if self.edited_pix:
            self._update_label_pixmap(self.edited_label, self.edited_pix)

    def _update_label_pixmap(self, label: QLabel, pix: QPixmap):
        if pix is None or pix.isNull():
            return
        scaled = pix.scaled(label.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.FastTransformation) #modificato in fasttransform talmodo che non fa l effetto blurrato nello scalare l'immagine
        label.setPixmap(scaled)


SPLASH_MESSAGES = [
    ("Inizializzazione del sistema...",      "#2753e0", 800),
    ("Facendo i complimenti al professore per un captatio benevolentiae...",            "#1c67de", 2000),
    ("Calcolando il senso della vita, l'universo e tutto quanto...", "#38d729", 2000),
    ("Verificando se P = NP.... in caso di crash allora P ≠ NP.", "#89b4fa", 2000),
    ("Dimostrando l'Ipotesi di Riemann...\n Ooops, i margini dello splash screen sono troppo stretti per scriverla.", "#f4df00", 2000),
    ("Avvio interfaccia grafica...",         "#ff497c", 600),
]
 
 
def build_fallback_pixmap() -> QPixmap:
    pix = QPixmap(700, 440)
    pix.fill(QColor("#0f0f1a"))
    painter = QPainter(pix)
    painter.setPen(QPen(QColor("#89b4fa")))
    painter.setFont(QFont("Georgia", 48, QFont.Weight.Bold))
    painter.drawText(pix.rect().adjusted(0, -60, 0, 0),
                     Qt.AlignmentFlag.AlignCenter, "JPEG Compressor")
    painter.setPen(QPen(QColor("#cdd6f4")))
    painter.setFont(QFont("Courier New", 12))
    painter.drawText(pix.rect().adjusted(0, 60, 0, 0),
                     Qt.AlignmentFlag.AlignCenter,
                     "Metodi del Calcolo Scientifico")
    painter.setPen(QPen(QColor("#e04444"), 2))
    painter.drawLine(0, 436, 700, 436)
 
    painter.end()
    return pix
 
 
def run_splash(app: QApplication) -> QSplashScreen:

    splash_pix = build_fallback_pixmap()
    splash = QSplashScreen(splash_pix)
    splash.setWindowTitle("BicoPeg-Splash") #nome random che ho messo perche mi serve un nome alla finestra per le regole su hyprland 
                                            #(con tiling attivo senza gestione float esce un po male)

    splash.setWindowFlags(
        Qt.WindowType.WindowStaysOnTopHint | 
        Qt.WindowType.FramelessWindowHint | 
        Qt.WindowType.SubWindow
    )

    screen = app.primaryScreen().geometry() # type: ignore
    size = splash.size()
    x = (screen.width() - size.width()) // 2
    y = (screen.height() - size.height()) // 2
    splash.move(x, y)
    
    splash.show()
    app.processEvents()
 
    for msg, color_hex, delay_ms in SPLASH_MESSAGES:

        splash.showMessage(
            f"{msg}\n\n",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            QColor(color_hex),
        )
        
        splash.repaint() 
        app.processEvents()
        
        QThread.msleep(delay_ms)
 
    return splash
 
 
def run_app(img_path: str, F: int, d: int):
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)  
 
    splash = run_splash(app)
    w = BitmapEditorApp(img_path, F, d)  
    w.show()
 
    splash.finish(w)          
    sys.exit(app.exec())



if __name__ == "__main__":
    run_app(img_path="", F=0, d=0)