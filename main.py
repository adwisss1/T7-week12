# ============================================================
# Nama  : [Baiq Adelia dwi Savitri]
# NIM   : [F1D02310006]
# Tugas : Tugas 6 — Visualisasi Data (PySide6 Dashboard)
# File  : main.py — Entry point aplikasi
# ============================================================

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

import data_loader as dl
from main_window import MainWindow


def load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())


def main() -> None:
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Dashboard Visualisasi Data")

    # 1. Inisialisasi database (buat jika belum ada)
    dl.init_db()

    # 2. Terapkan stylesheet
    load_stylesheet(app)

    # 3. Tampilkan jendela utama
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
