# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Kelas]
# Tugas : Tugas 6 — Visualisasi Data (PySide6 Dashboard)
# File  : chart_widget.py — Widget chart Matplotlib untuk PySide6
# ============================================================

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")                         # renderer non-interaktif (wajib sebelum pyplot)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt

import data_loader as dl


# ── Palet warna konsisten ─────────────────────────────────────────────────────
COLORS = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
          "#59a14f", "#edc948", "#b07aa1", "#ff9da7"]


class ChartCanvas(FigureCanvas):
    """Canvas Matplotlib yang bisa ditempel langsung ke layout Qt."""
        
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=96,
                                          facecolor="#1e1e2e")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._style_ax()

    def _style_ax(self):
        self.fig.patch.set_facecolor("#ffffff") # Mengubah warna luar canvas jadi putih
        self.ax.set_facecolor("#ffffff")        # Mengubah warna dalam chart jadi putih
        self.ax.tick_params(colors="#1e1e2e", labelsize=8) # Teks skala jadi gelap
        for spine in self.ax.spines.values():
            spine.set_edgecolor("#dadce0")      # Garis tepi chart jadi abu-abu terang

    def clear(self):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        self._style_ax()

    def draw_bar(self, series: pd.Series, title: str, xlabel: str, ylabel: str):
        """Bar chart horizontal."""
        self.clear()
        bars = self.ax.barh(series.index, series.values, color=COLORS[:len(series)])
        self.ax.bar_label(bars, fmt="%.0f", color="#cdd6f4", fontsize=7, padding=3)
        self.ax.set_title(title, color="#cdd6f4", fontsize=10, pad=8)
        self.ax.set_xlabel(xlabel, color="#a6adc8", fontsize=8)
        self.ax.set_ylabel(ylabel, color="#a6adc8", fontsize=8)
        self.ax.invert_yaxis()
        self.fig.tight_layout()
        self.draw()

    def draw_line(self, series: pd.Series, title: str, xlabel: str, ylabel: str):
        """Line chart tren waktu."""
        self.clear()
        self.ax.plot(series.index, series.values, color=COLORS[0],
                     linewidth=1.5, marker="o", markersize=3)
        self.ax.fill_between(series.index, series.values, alpha=0.15, color=COLORS[0])
        self.ax.set_title(title, color="#cdd6f4", fontsize=10, pad=8)
        self.ax.set_xlabel(xlabel, color="#a6adc8", fontsize=8)
        self.ax.set_ylabel(ylabel, color="#a6adc8", fontsize=8)
        self.ax.tick_params(axis="x", rotation=30, labelsize=7)
        self.fig.tight_layout()
        self.draw()

    def draw_pie(self, series: pd.Series, title: str):
        """Pie chart distribusi."""
        self.clear()
        wedges, texts, autotexts = self.ax.pie(
            series.values,
            labels=series.index,
            autopct="%1.1f%%",
            colors=COLORS[:len(series)],
            startangle=90,
            pctdistance=0.8,
        )
        for t in texts:
            t.set_color("#cdd6f4")
            t.set_fontsize(7)
        for at in autotexts:
            at.set_color("#1e1e2e")
            at.set_fontsize(7)
        self.ax.set_title(title, color="#cdd6f4", fontsize=10, pad=8)
        self.fig.tight_layout()
        self.draw()

    def draw_scatter(self, df: pd.DataFrame, title: str):
        """Scatter plot harga vs total per kategori."""
        self.clear()
        for i, (kat, grp) in enumerate(df.groupby("kategori")):
            self.ax.scatter(grp["harga"], grp["total"],
                            color=COLORS[i % len(COLORS)], s=18,
                            alpha=0.7, label=kat)
        self.ax.set_title(title, color="#cdd6f4", fontsize=10, pad=8)
        self.ax.set_xlabel("Harga Satuan (Rp)", color="#a6adc8", fontsize=8)
        self.ax.set_ylabel("Total (Rp)", color="#a6adc8", fontsize=8)
        legend = self.ax.legend(fontsize=6, loc="upper left",
                                facecolor="#313244", edgecolor="#45475a")
        for text in legend.get_texts():
            text.set_color("#cdd6f4")
        self.fig.tight_layout()
        self.draw()

    def save_png(self, path: str):
        self.fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=self.fig.get_facecolor())


# ── Panel chart lengkap dengan kontrol ───────────────────────────────────────

CHART_TYPES = {
    "Bar — Total per Kategori": "bar",
    "Line — Tren Waktu": "line",
    "Pie — Distribusi Jumlah": "pie",
    "Scatter — Harga vs Total": "scatter",
}


class ChartPanel(QWidget):
    """Widget panel yang berisi selector tipe chart, canvas, dan tombol export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._df: pd.DataFrame = pd.DataFrame()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # ── Toolbar ────────────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        lbl = QLabel("Tipe Chart:")
        lbl.setStyleSheet("color:#cdd6f4; font-size:13px;")
        toolbar.addWidget(lbl)

        self.combo = QComboBox()
        self.combo.addItems(CHART_TYPES.keys())
        self.combo.setFixedWidth(240)
        self.combo.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.combo)

        toolbar.addStretch()

        btn_refresh = QPushButton("🔄  Refresh Chart")
        btn_refresh.setObjectName("btnRefresh")
        btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(btn_refresh)

        btn_export = QPushButton("💾  Export PNG")
        btn_export.setObjectName("btnExport")
        btn_export.clicked.connect(self._export_png)
        toolbar.addWidget(btn_export)

        root.addLayout(toolbar)

        # ── Canvas ─────────────────────────────────────────────────────────
        self.canvas = ChartCanvas()
        root.addWidget(self.canvas)

    # ── Public API ────────────────────────────────────────────────────────

    def load_data(self, df: pd.DataFrame):
        self._df = df
        self.refresh()

    def refresh(self):
        if self._df.empty:
            return
        chart_key = self.combo.currentText()
        ctype = CHART_TYPES.get(chart_key, "bar")
        df = self._df

        if ctype == "bar":
            self.canvas.draw_bar(
                dl.get_total_per_kategori(df),
                "Total Pendapatan per Kategori",
                "Total (Rp)", "Kategori",
            )
        elif ctype == "line":
            self.canvas.draw_line(
                dl.get_total_per_tanggal(df),
                "Tren Pendapatan Harian",
                "Tanggal", "Total (Rp)",
            )
        elif ctype == "pie":
            self.canvas.draw_pie(
                dl.get_distribusi_jumlah(df),
                "Distribusi Jumlah Item per Kategori",
            )
        elif ctype == "scatter":
            self.canvas.draw_scatter(df, "Harga Satuan vs Total Transaksi")

    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Chart sebagai PNG", "chart.png", "PNG Files (*.png)"
        )
        if path:
            self.canvas.save_png(path)
