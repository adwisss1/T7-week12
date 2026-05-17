# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Kelas]
# Tugas : Tugas 6 — Visualisasi Data (PySide6 Dashboard)
# File  : crud_dialog.py — Dialog CRUD untuk tambah / ubah data
# ============================================================

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLabel,
)
from PySide6.QtCore import Qt
import data_loader as dl


class RowDialog(QDialog):
    """Dialog untuk tambah atau ubah satu baris data penjualan."""

    def __init__(self, parent=None, row_data: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Data" if row_data is None else "Edit Data")
        self.setMinimumWidth(360)
        self._build_ui(row_data)

    def _build_ui(self, row_data: dict | None):
        form = QFormLayout(self)
        form.setSpacing(10)

        # Tanggal
        self.inp_tanggal = QLineEdit()
        self.inp_tanggal.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Tanggal:", self.inp_tanggal)

        # Kategori
        self.inp_kategori = QComboBox()
        self.inp_kategori.addItems(dl.CATEGORIES)
        form.addRow("Kategori:", self.inp_kategori)

        # Produk
        self.inp_produk = QLineEdit()
        form.addRow("Produk:", self.inp_produk)

        # Jumlah
        self.inp_jumlah = QSpinBox()
        self.inp_jumlah.setRange(1, 9999)
        form.addRow("Jumlah:", self.inp_jumlah)

        # Harga
        self.inp_harga = QDoubleSpinBox()
        self.inp_harga.setRange(0.01, 99_999_999)
        self.inp_harga.setDecimals(2)
        self.inp_harga.setPrefix("Rp ")
        form.addRow("Harga Satuan:", self.inp_harga)

        # Isi data awal jika mode edit
        if row_data:
            self.inp_tanggal.setText(str(row_data.get("tanggal", "")))
            idx = self.inp_kategori.findText(row_data.get("kategori", ""))
            if idx >= 0:
                self.inp_kategori.setCurrentIndex(idx)
            self.inp_produk.setText(str(row_data.get("produk", "")))
            self.inp_jumlah.setValue(int(row_data.get("jumlah", 1)))
            self.inp_harga.setValue(float(row_data.get("harga", 0)))

        # Tombol OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_values(self) -> dict:
        return {
            "tanggal":  self.inp_tanggal.text().strip(),
            "kategori": self.inp_kategori.currentText(),
            "produk":   self.inp_produk.text().strip(),
            "jumlah":   self.inp_jumlah.value(),
            "harga":    self.inp_harga.value(),
        }
