"""Small optional PySide6 shell; core rendering remains usable headlessly."""
from __future__ import annotations

try:
    from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QPushButton, QSpinBox, QDoubleSpinBox, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - exercised only on installations without GUI extras
    QApplication = None


def run() -> int:
    if QApplication is None:
        raise RuntimeError("PySide6 ist nicht installiert; installiere flightanimation[gui]")
    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    window.setWindowTitle("Flight Animation")
    central, layout = QWidget(), QVBoxLayout()
    info = QLabel("Keine KML-Datei geladen")
    choose = QPushButton("FR24-KML auswählen")
    choose.clicked.connect(lambda: info.setText(QFileDialog.getOpenFileName(window, "KML auswählen", filter="KML (*.kml)")[0] or info.text()))
    duration = QDoubleSpinBox(); duration.setRange(0.1, 3600); duration.setValue(5.0); duration.setSuffix(" s")
    fps = QSpinBox(); fps.setRange(25, 30); fps.setValue(25)
    for widget in (choose, info, duration, fps): layout.addWidget(widget)
    central.setLayout(layout); window.setCentralWidget(central); window.resize(500, 240); window.show()
    return app.exec()
