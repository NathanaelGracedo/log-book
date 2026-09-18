# Desain Antarmuka Web (UI) Dashboard Log Book Magang Polinema

## 1. Ringkasan & Tujuan
Ekstensi antarmuka pengguna berbasis web (*Local Web Dashboard*) untuk sistem otomatisasi Log Book Magang Industri Polinema di PT Naraya Telematika. 

Antarmuka ini mempermudah pengguna dalam:
1. Memantau progres kelengkapan log book harian periode Juli–Desember 2026 secara visual.
2. Mengisi dan mengedit catatan harian tanpa mengedit file YAML secara manual.
3. Mengembangkan poin kegiatan singkat menjadi narasi industri formal dengan 1 tombol (*Formalize*).
4. Melengkapi sisa hari kosong secara massal (*Batch Auto-Fill*) dengan kurikulum tugas IT realistis.
5. Memperbarui profil mahasiswa dan dosen/pembimbing lapangan langsung dari UI.
6. Memicu kompilasi XeLaTeX dan membaca pratinjau PDF langsung di peramban web (*Live PDF Preview*).

---

## 2. Arsitektur Sistem

```text
log-book/
├── web/
│   ├── __init__.py
│   ├── app.py                   # FastAPI REST API & Static Server
│   └── static/
│       ├── index.html           # SPA Dashboard HTML5
│       ├── styles.css           # Vanilla CSS Design System (Bento, Dark Mode, Tokens)
│       └── app.js               # Frontend Client Logic (Fetch API, Reactive State)
├── main.py                      # CLI entrypoint (support flag: python3 main.py --ui)
├── scripts/                     # Modul logika inti yang sudah ada
│   ├── calendar_utils.py
│   ├── data_manager.py
│   ├── narrative_expander.py
│   └── latex_builder.py
└── docs/superpowers/specs/
    └── 2026-09-18-logbook-web-ui-design.md
```

---

## 3. Spesifikasi REST API (Backend FastAPI)

Backend dibangun menggunakan **FastAPI** dan dijalankan melalui **Uvicorn**.

### 3.1 Endpoints
1. `GET /api/calendar`
   - **Deskripsi**: Mengambil seluruh kalender magang (27 minggu, 6 bulan) lengkap dengan status pengisian per tanggal, catatan kegiatan, dan ringkasan progres total.
   - **Response**:
     ```json
     {
       "total_days": 155,
       "filled_days": 25,
       "missing_days": 130,
       "percentage": 16.1,
       "months": [
         {
           "month_index": 1,
           "name": "Juli 2026",
           "filled_count": 4,
           "total_count": 27,
           "weeks": [ ... ]
         }
       ]
     }
     ```

2. `POST /api/save-day`
   - **Request Body**: `{"date": "2026-08-03", "note": "Melakukan testing API auth"}`
   - **Deskripsi**: Menyimpan catatan kegiatan pada file `data/bulan_XX.yaml` yang sesuai dan mengembalikan status sukses.

3. `POST /api/formalize`
   - **Request Body**: `{"note": "testing api auth postman"}`
   - **Deskripsi**: Mengonversi poin singkat menjadi narasi formal menggunakan fungsi `expand_narrative()`.
   - **Response**: `{"formalized": "Melaksanakan pengujian endpoint API authentication menggunakan Postman dan mendokumentasikan respon kode status HTTP."}`

4. `POST /api/batch-autofill`
   - **Request Body**: `{"overwrite_existing": false}`
   - **Deskripsi**: Mengisi secara otomatis seluruh hari aktif yang masih kosong dengan kurikulum kegiatan IT PT Naraya Telematika (onboarding, feature development, database indexing, testing, refactoring, sprint review). Hari yang sudah diisi manual tidak akan ditimpa.

5. `POST /api/generate-pdf`
   - **Request Body**: `{"target": "all" | "cumulative" | 1 | 2 | 3 | 4 | 5 | 6}`
   - **Deskripsi**: Menjalankan pipeline kompilasi `xelatex` dan mengembalikan URL berkas PDF yang dihasilkan.
   - **Response**: `{"status": "ok", "pdf_url": "/api/pdf/Logbook_01_Juli_2026.pdf"}`

6. `GET /api/pdf/{filename}`
   - **Deskripsi**: Menyajikan berkas PDF dari folder `output/` untuk ditampilkan di peramban web (inline content-disposition).

7. `GET /api/config` & `POST /api/config`
   - **Deskripsi**: Membaca dan memperbarui isi konfigurasi identitas di `config.yaml`.

---

## 4. Spesifikasi Frontend (UI/UX Pro Max)

Frontend mengimplementasikan standar desain modern tanpa ketergantungan paket Node.js yang berat:

### 4.1 Desain Sistem (Tokens)
- **Primary Color**: `#2563EB` (Polinema Academic Blue)
- **Accent / Success Color**: `#059669` (Emerald Green)
- **Warning Color**: `#D97706` (Amber untuk hari kosong)
- **Theme Support**: Auto Light / Dark Mode (`data-theme="dark"`).
- **Typography**: Google Fonts Inter / Fira Sans.
- **Micro-animations**: Transisi halus 150–250ms (hover, modal dialog popup).

### 4.2 Komponen Utama
1. **Header & Progress Bar**:
   - Menampilkan judul aplikasi dan progres kelengkapan: `XX / 155 Hari Terisi (YY%)`.
   - Tombol aksi: `⚡ Lengkapi Hari Kosong`, `📄 Generate PDF`, `⚙️ Profil`, `🌓 Ganti Tema`.
2. **Tab Navigasi Bulan**:
   - Filter cepat untuk beralih antara bulan Juli, Agustus, September, Oktober, November, Desember, atau Semua Bulan.
   - Tombol toggle filter: `Semua` | `Belum Diisi` (jump langsung ke hari bolong) | `Sudah Diisi`.
3. **Weekly Bento Cards**:
   - Kartu mingguan yang menampilkan tabel hari (Senin s/d Sabtu).
   - Badge jam kerja: `08.00 - 16.00` (Senin–Jumat) dan `08.00 - 14.00` (Sabtu).
   - Pratinjau narasi kegiatan dan tombol cepat `Edit`.
4. **Modal Editor Kegiatan**:
   - Input catatan kegiatan dengan dukungan tombol `⚡ Formalize Narasi` dan `💡 Beri Saran Kegiatan`.
   - Tombol Simpan yang langsung memperbarui state tanpa me-refresh halaman.
5. **Modal PDF Previewer**:
   - Pemilihan bulan (1 s/d 6 atau Lengkap Kumulatif).
   - Pemicu kompilasi XeLaTeX dan tampilan pratinjau PDF langsung di dalam iframe peramban.

---

## 5. Rencana Pengujian & Verifikasi
1. **Instalasi Dependensi**: Verifikasi `fastapi` dan `uvicorn` terpasang dan berjalan di lingkungan Python.
2. **API Testing**:
   - Pengujian `GET /api/calendar` mengembalikan 155 hari kerja aktif 2026.
   - Pengujian `POST /api/save-day` memperbarui file `data/bulan_XX.yaml` dengan benar.
   - Pengujian `POST /api/formalize` mengubah input informal menjadi narasi resmi.
   - Pengujian `POST /api/batch-autofill` mengisi hari kosong tanpa merusak catatan yang sudah ada.
3. **UI Testing**:
   - Pengujian visual di browser: rendering kartu mingguan, responsivitas tema gelap/terang, dan interaktivitas modal editor.
   - Pengujian kompilasi PDF dan pratinjau PDF di iframe.
4. **CLI Integration**:
   - Pengujian perintah `python3 main.py --ui` berhasil menyalakan server uvicorn dan menampilkan alamat dashboard.
