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

SPLASH_MESSAGES = [
    ("Inizializzazione del sistema...",      "#2753e0", 800),
    ("Facendo i complimenti al professore per un captatio benevolentiae...",            "#1c67de", 1300),
    ("Calcolando il senso della vita, l'universo e tutto quanto...", "#38d729", 1300),
    ("Verificando se P = NP.... in caso di crash allora P ≠ NP.", "#89b4fa", 1300),
    ("Dimostrando l'Ipotesi di Riemann...\n Ooops, i margini dello splash screen sono troppo stretti per scriverla.", "#f4df00", 1300),
    ("Depositando un caco su un palco famoso...", "#1c97de", 1000),
    ("Avvio interfaccia grafica...",         "#ff497c", 600),
]
 