# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Kelas]
# Tugas : Tugas 6 — Visualisasi Data (PySide6 Dashboard)
# File  : main_window.py — Jendela utama dashboard
# ============================================================

import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QComboBox, QPushButton, QFrame, QMessageBox,
    QAbstractItemView, QStatusBar,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

import data_loader as dl
from chart_widget import ChartPanel
from crud_dialog import RowDialog


# ── Kartu ringkasan kecil ─────────────────────────────────────────────────────

class SummaryCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("summaryCard")
        self.setMinimumWidth(160)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(2)

        self._title = QLabel(title)
        self._title.setObjectName("cardTitle")
        lay.addWidget(self._title)

        self._value = QLabel("—")
        self._value.setObjectName("cardValue")
        lay.addWidget(self._value)

    def set_value(self, val: str):
        self._value.setText(val)


# ── Jendela utama ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Visualisasi Data — Supermarket Sales")
        self.resize(1280, 760)
        self._current_df: pd.DataFrame = pd.DataFrame()
        self._build_ui()
        self._load_and_refresh()

    # ── Konstruksi UI ────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Header
        root.addWidget(self._make_header())

        # Summary cards
        self._cards: dict[str, SummaryCard] = {}
        root.addLayout(self._make_card_row())

        # Filter bar
        root.addWidget(self._make_filter_bar())

        # Splitter: tabel kiri | chart kanan
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._make_table_panel())
        splitter.addWidget(self._make_chart_panel())
        splitter.setSizes([540, 700])
        root.addWidget(splitter, stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _make_header(self) -> QLabel:
        lbl = QLabel("📊  Dashboard Visualisasi Data Supermarket")
        lbl.setObjectName("header")
        return lbl

    def _make_card_row(self) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.setSpacing(10)
        specs = [
            ("total_transaksi",  "Total Transaksi"),
            ("total_pendapatan", "Total Pendapatan"),
            ("rata_rata_total",  "Rata-rata per Transaksi"),
            ("kategori_terlaris","Kategori Terlaris"),
        ]
        for key, title in specs:
            card = SummaryCard(title)
            self._cards[key] = card
            lay.addWidget(card)
        return lay

    def _make_filter_bar(self) -> QWidget:
        bar = QWidget()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        lbl = QLabel("Filter Kategori:")
        lbl.setStyleSheet("color:#cdd6f4; font-size:13px;")
        lay.addWidget(lbl)

        self.combo_filter = QComboBox()
        self.combo_filter.addItem("Semua")
        self.combo_filter.addItems(dl.CATEGORIES)
        self.combo_filter.setFixedWidth(220)
        self.combo_filter.currentTextChanged.connect(self._on_filter_changed)
        lay.addWidget(self.combo_filter)

        lay.addStretch()

        for label, slot, obj in [
            ("➕  Tambah", self._on_add,    "btnAdd"),
            ("✏️  Edit",   self._on_edit,   "btnEdit"),
            ("🗑️  Hapus",  self._on_delete, "btnDelete"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName(obj)
            btn.clicked.connect(slot)
            lay.addWidget(btn)

        return bar

    def _make_table_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lbl = QLabel("Data Transaksi")
        lbl.setObjectName("panelTitle")
        lay.addWidget(lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tanggal", "Kategori", "Produk", "Jumlah", "Harga (Rp)", "Total (Rp)"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

        return panel

    def _make_chart_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lbl = QLabel("Visualisasi Chart")
        lbl.setObjectName("panelTitle")
        lay.addWidget(lbl)

        self.chart_panel = ChartPanel()
        lay.addWidget(self.chart_panel)

        return panel

    # ── Logika data ──────────────────────────────────────────────────────

    def _load_and_refresh(self, kategori: str = "Semua"):
        self._current_df = dl.fetch_all(kategori)
        self._populate_table(self._current_df)
        self._update_cards(self._current_df)
        self.chart_panel.load_data(self._current_df)
        self.status.showMessage(
            f"Menampilkan {len(self._current_df)} baris  |  Filter: {kategori}"
        )

    def _populate_table(self, df: pd.DataFrame):
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            r = self.table.rowCount()
            self.table.insertRow(r)
            values = [
                str(int(row["id"])),
                str(row["tanggal"]),
                str(row["kategori"]),
                str(row["produk"]),
                str(int(row["jumlah"])),
                f"{row['harga']:,.2f}",
                f"{row['total']:,.2f}",
            ]
            for c, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

    def _update_cards(self, df: pd.DataFrame):
        s = dl.get_summary(df)
        self._cards["total_transaksi"].set_value(f"{s['total_transaksi']:,}")
        self._cards["total_pendapatan"].set_value(f"Rp {s['total_pendapatan']:,.0f}")
        self._cards["rata_rata_total"].set_value(f"Rp {s['rata_rata_total']:,.0f}")
        self._cards["kategori_terlaris"].set_value(s["kategori_terlaris"])

    # ── Slot / event handler ─────────────────────────────────────────────

    def _on_filter_changed(self, text: str):
        self._load_and_refresh(text)

    def _on_add(self):
        dlg = RowDialog(self)
        if dlg.exec():
            v = dlg.get_values()
            dl.insert_row(v["tanggal"], v["kategori"], v["produk"], v["jumlah"], v["harga"])
            self._load_and_refresh(self.combo_filter.currentText())

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Baris", "Pilih baris yang ingin diedit terlebih dahulu.")
            return
        row_id = int(self.table.item(row, 0).text())
        row_data = self._current_df[self._current_df["id"] == row_id].iloc[0].to_dict()
        dlg = RowDialog(self, row_data)
        if dlg.exec():
            v = dlg.get_values()
            dl.update_row(row_id, v["tanggal"], v["kategori"], v["produk"], v["jumlah"], v["harga"])
            self._load_and_refresh(self.combo_filter.currentText())

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Baris", "Pilih baris yang ingin dihapus terlebih dahulu.")
            return
        row_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus baris dengan ID {row_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            dl.delete_row(row_id)
            self._load_and_refresh(self.combo_filter.currentText())
