# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Kelas]
# Tugas : Tugas 6 — Visualisasi Data (PySide6 Dashboard)
# File  : data_loader.py — Modul pemuatan dan pemrosesan data
# ============================================================

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "supermarket.db")

CATEGORIES = ["Electronic accessories", "Fashion accessories", "Food and beverages",
               "Health and beauty", "Home and lifestyle", "Sports and travel"]

PRODUCT_MAP = {
    "Electronic accessories": ["USB Cable", "Earphones", "Phone Stand", "Power Bank", "Screen Protector"],
    "Fashion accessories":    ["Sunglasses", "Belt", "Watch", "Bracelet", "Handbag"],
    "Food and beverages":     ["Coffee", "Juice", "Snack Pack", "Mineral Water", "Chocolate"],
    "Health and beauty":      ["Shampoo", "Face Wash", "Lotion", "Perfume", "Vitamins"],
    "Home and lifestyle":     ["Air Freshener", "Pillow", "Towel", "Candle", "Storage Box"],
    "Sports and travel":      ["Yoga Mat", "Water Bottle", "Cap", "Backpack", "Running Shoes"],
}


def init_db() -> None:
    """Buat database SQLite dan isi dengan data contoh jika belum ada."""
    import random
    from datetime import date, timedelta

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS penjualan (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal  TEXT    NOT NULL,
            kategori TEXT    NOT NULL,
            produk   TEXT    NOT NULL,
            jumlah   INTEGER NOT NULL,
            harga    REAL    NOT NULL,
            total    REAL    GENERATED ALWAYS AS (jumlah * harga) STORED
        )
    """)

    cur.execute("SELECT COUNT(*) FROM penjualan")
    if cur.fetchone()[0] == 0:
        random.seed(42)
        base = date(2023, 1, 1)
        rows = []
        for i in range(300):
            tgl = (base + timedelta(days=random.randint(0, 364))).isoformat()
            kat = random.choice(CATEGORIES)
            prod = random.choice(PRODUCT_MAP[kat])
            qty = random.randint(1, 10)
            harga = round(random.uniform(10_000, 500_000), 2)
            rows.append((tgl, kat, prod, qty, harga))
        cur.executemany(
            "INSERT INTO penjualan (tanggal, kategori, produk, jumlah, harga) VALUES (?,?,?,?,?)",
            rows,
        )
        conn.commit()

    conn.close()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def fetch_all(kategori: str = "Semua") -> pd.DataFrame:
    """Ambil semua baris, opsional filter per kategori."""
    conn = sqlite3.connect(DB_PATH)
    if kategori == "Semua":
        df = pd.read_sql_query(
            "SELECT id, tanggal, kategori, produk, jumlah, harga, total FROM penjualan ORDER BY tanggal",
            conn,
        )
    else:
        df = pd.read_sql_query(
            "SELECT id, tanggal, kategori, produk, jumlah, harga, total FROM penjualan "
            "WHERE kategori = ? ORDER BY tanggal",
            conn,
            params=(kategori,),
        )
    conn.close()
    return df


def insert_row(tanggal: str, kategori: str, produk: str, jumlah: int, harga: float) -> None:
    """Tambah satu baris data."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO penjualan (tanggal, kategori, produk, jumlah, harga) VALUES (?,?,?,?,?)",
        (tanggal, kategori, produk, jumlah, harga),
    )
    conn.commit()
    conn.close()


def update_row(row_id: int, tanggal: str, kategori: str, produk: str, jumlah: int, harga: float) -> None:
    """Ubah data baris berdasarkan id."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE penjualan SET tanggal=?, kategori=?, produk=?, jumlah=?, harga=? WHERE id=?",
        (tanggal, kategori, produk, jumlah, harga, row_id),
    )
    conn.commit()
    conn.close()


def delete_row(row_id: int) -> None:
    """Hapus data baris berdasarkan id."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM penjualan WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


# ── Ringkasan ─────────────────────────────────────────────────────────────────

def get_summary(df: pd.DataFrame) -> dict:
    """Hitung statistik ringkasan dari dataframe."""
    return {
        "total_transaksi": len(df),
        "total_pendapatan": df["total"].sum() if not df.empty else 0,
        "rata_rata_total": df["total"].mean() if not df.empty else 0,
        "kategori_terlaris": (
            df.groupby("kategori")["total"].sum().idxmax() if not df.empty else "-"
        ),
    }


def get_total_per_kategori(df: pd.DataFrame) -> pd.Series:
    """Total pendapatan per kategori."""
    return df.groupby("kategori")["total"].sum().sort_values(ascending=False)


def get_total_per_tanggal(df: pd.DataFrame) -> pd.Series:
    """Total pendapatan per tanggal (tren waktu)."""
    df = df.copy()
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.groupby("tanggal")["total"].sum().sort_index()


def get_distribusi_jumlah(df: pd.DataFrame) -> pd.Series:
    """Distribusi jumlah item terjual per kategori (untuk pie chart)."""
    return df.groupby("kategori")["jumlah"].sum()
