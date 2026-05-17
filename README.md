# T7-week12 — Dashboard Visualisasi Data (PySide6)

**Tugas 6 Praktikum PySide6** 
— Buat aplikasi dashboard yang menampilkan data tabular, ringkasan, filter, dan chart Matplotlib.

---

## Deskripsi Tugas

Aplikasi ini adalah **dashboard visualisasi data penjualan supermarket** yang dibangun menggunakan **PySide6** dan **Matplotlib**. Data disimpan di database **SQLite** lokal dan mendukung operasi **CRUD** penuh.

---

## Struktur Project (Separation of Concerns)

```
T7-week12/
├── main.py           # Entry point — inisialisasi app & jendela
├── main_window.py    # View utama — layout dashboard, tabel, kartu ringkasan
├── chart_widget.py   # Widget chart — 4 jenis chart Matplotlib (bar, line, pie, scatter)
├── crud_dialog.py    # Dialog CRUD — form tambah & edit data
├── data_loader.py    # Model/data layer — SQLite CRUD & fungsi agregasi pandas
├── styles.qss        # Stylesheet — tema dark Catppuccin Mocha
└── supermarket.db    # Database SQLite (dibuat otomatis saat pertama dijalankan)
```

### Prinsip SOC yang Diterapkan

| File | Tanggung Jawab |
|---|---|
| `main.py` | Bootstrap aplikasi, inisialisasi DB, load stylesheet |
| `main_window.py` | Tampilan & interaksi jendela utama (Controller + View) |
| `chart_widget.py` | Semua logika rendering chart Matplotlib |
| `crud_dialog.py` | Form input data (Add/Edit) |
| `data_loader.py` | Akses database SQLite, query pandas, fungsi agregasi |
| `styles.qss` | Semua definisi visual/tema |

---

## Fitur yang Diimplementasikan

### Wajib
- [x] **Data minimal 50 baris** — 300 baris data dummy otomatis dibuat saat pertama jalan
- [x] **QTableWidget** — menampilkan semua kolom data penjualan
- [x] **Minimal 2 jenis chart** — Bar, Line, Pie, Scatter (total 4 pilihan)
- [x] **Filter kategori** — dropdown memfilter tabel & chart sekaligus
- [x] **Tombol Refresh Chart** — update ulang visualisasi
- [x] **Tombol Export PNG** — simpan chart sebagai file gambar

### Bonus — SQLite CRUD
- [x] **Tambah data** — tombol ➕ Tambah dengan dialog form
- [x] **Edit data** — tombol ✏️ Edit pada baris yang dipilih
- [x] **Hapus data** — tombol 🗑️ Hapus dengan konfirmasi
- [x] **Refresh otomatis** — dashboard (tabel + chart + kartu) diperbarui setelah setiap operasi CRUD

---

## Struktur Database SQLite

**File:** `supermarket.db`  
**Tabel:** `penjualan`

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER | Primary key, auto increment |
| `tanggal` | TEXT | Format YYYY-MM-DD |
| `kategori` | TEXT | Kategori produk |
| `produk` | TEXT | Nama produk |
| `jumlah` | INTEGER | Jumlah item terjual |
| `harga` | REAL | Harga satuan (Rp) |
| `total` | REAL | Kolom virtual: jumlah × harga |

**Kategori yang tersedia:**
- Electronic accessories
- Fashion accessories
- Food and beverages
- Health and beauty
- Home and lifestyle
- Sports and travel

---

## Cara Menjalankan

### 1. Install dependencies

```bash
pip install PySide6 pandas matplotlib
```

### 2. Jalankan aplikasi

```bash
cd T7-week12
python main.py
```

Database `supermarket.db` akan **dibuat otomatis** dengan 300 baris data saat pertama dijalankan.

---

## Screenshot Aplikasi

*(Tambahkan screenshot setelah menjalankan aplikasi)*

- `screenshot_dashboard` — Tampilan utama dashboard
- `screenshot_filter` — Filter per kategori
- `screenshot_crud` — Dialog tambah/edit data
- `screenshot_chart_` — Berbagai jenis chart

---

