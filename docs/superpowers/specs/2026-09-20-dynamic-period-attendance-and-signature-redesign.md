# Desain Dinamisasi Periode Magang, Status Kehadiran, dan Redesain Tanda Tangan

## 1. Ringkasan & Tujuan
Spesifikasi peningkatan fleksibilitas sistem Log Book Magang Industri JTI Polinema:
1. **Dinamisasi Periode Magang**: Mendukung kustomisasi tanggal mulai dan tanggal selesai magang secara penuh (tidak lagi di-hardcode Juli–Desember 2026).
2. **Fleksibilitas Hari Kerja**: Mendukung jadwal 5 hari kerja (Senin–Jumat, baris Sabtu dihilangkan dari tabel) maupun 6 hari kerja (Senin–Sabtu).
3. **Status Kehadiran Khusus & Font Merah**: Mendukung pencatatan status `Hadir`, `Izin`, `Sakit`, `Cuti`, dan `Libur Nasional`. Jika berstatus selain Hadir, jam masuk/pulang otomatis diset `-` dan teks kegiatan dicetak dengan warna font **merah**.
4. **Redesain Tata Letak Tanda Tangan**: Mengubah tata letak tanda tangan 3-kolom sejajar menjadi tata letak 2 tingkat (Mahasiswa di kanan atas; *Mengetahui* di tengah; Dosen Pembimbing di kiri bawah dan Pembimbing Lapangan di kanan bawah), serta menghapus label NIM, NIP, dan NIK pada seluruh bagian tanda tangan.
5. **Setup Wizard & Integrasi Web UI**: Memandu konfigurasi awal di terminal serta menyediakan antarmuka form interaktif di Web UI Dashboard.

---

## 2. Skema Konfigurasi & Data

### 2.1 Konfigurasi (`config.yaml` & `config.example.yaml`)
```yaml
mahasiswa:
  nama: "Nama Lengkap Mahasiswa"
  nim: "XXXXXXXXXX"
  prodi: "Sarjana Terapan Teknik Informatika"
  mitra: "Nama Perusahaan / Tempat Magang"

periode:
  tanggal_mulai: "2026-07-01"    # Format YYYY-MM-DD
  tanggal_selesai: "2026-12-31"  # Format YYYY-MM-DD

pengaturan:
  hari_kerja: "senin_sabtu"      # Pilihan: "senin_jumat" (5 hari) atau "senin_sabtu" (6 hari)
  jam_kerja:
    senin_jumat:
      masuk: "08.00"
      pulang: "16.00"
    sabtu:
      masuk: "08.00"
      pulang: "14.00"

pembimbing:
  dosen:
    nama: "Nama Dosen Pembimbing, S.Kom., M.Kom."
    nip: "198XXXXXXXXXXXX"
  lapangan:
    nama: "Nama Pembimbing Lapangan / Mentor"
    nik: "NIK / ID Karyawan"
```

### 2.2 Format Catatan Kegiatan (`data/*.yaml`)
Mendukung format string sederhana (default hadir) dan format objek status:
```yaml
bulan: 8
tahun: 2026
catatan:
  # Hadir biasa (format string langsung)
  "2026-08-03": "Melakukan implementasi fitur autentikasi OAuth2"

  # Status khusus (format dict)
  "2026-08-04":
    status: "izin"               # "hadir" | "izin" | "sakit" | "cuti" | "libur"
    kegiatan: "Izin mengikuti kegiatan akademik yudisium di kampus"
```

---

## 3. Logika Kalender & Bundling Dinamis (`scripts/calendar_utils.py`)

1. **Jangkauan Kalender Dinamis**:
   - Menghitung hari kerja aktif antara `tanggal_mulai` dan `tanggal_selesai`.
   - Mengabaikan hari Minggu.
   - Jika `hari_kerja == "senin_jumat"`: hari Sabtu turut diabaikan. Minggu kerja berakhir di hari Jumat. Tabel mingguan berisi maksimal 5 baris.
   - Jika `hari_kerja == "senin_sabtu"`: hari Sabtu disertakan (jam pulang default `14.00`). Minggu kerja berakhir di hari Sabtu. Tabel mingguan berisi maksimal 6 baris.
2. **Bundling Bulanan Berdasarkan Bulan Kalender Nyata**:
   - Mendeteksi seluruh bulan kalender nyata yang dilalui dalam rentang magang.
   - Mengelompokkan minggu ke dalam bundel bulan dominan.
   - Menghasilkan nama berkas PDF otomatis: `Logbook_01_<NamaBulan>_<Tahun>.pdf`, dst., serta berkas kumulatif `Logbook_Lengkap.pdf`.

---

## 4. Spesifikasi Rendering Dokumen LaTeX (`scripts/latex_builder.py`)

### 4.1 Header Kop Surat Resmi
- **Kiri (`0.15\textwidth`)**: Logo Polinema (`height=1.8cm`).
- **Tengah (`0.70\textwidth`)**: Teks resmi instansi Polinema JTI terpusat (`\centering`).
- **Kanan (`0.15\textwidth`)**: Kolom kosong penyeimbang (`\hfill`).

### 4.2 Baris Tabel Kegiatan & Teks Merah
- Menyertakan paket `\usepackage{xcolor}` di `templates/logbook_template.tex`.
- Penentuan jam & warna font:
  - Jika status `hadir`: jam masuk `08.00`, pulang `16.00` (atau `14.00` hari Sabtu), font kegiatan hitam standar.
  - Jika status `izin`, `sakit`, `cuti`, atau `libur`:
    - Jam Masuk: `-`
    - Jam Pulang: `-`
    - Kolom Kegiatan: `\textcolor{red}{\textbf{[{STATUS}]}: {Catatan Alasan}}` (contoh: `\textcolor{red}{\textbf{[IZIN]:} Mengikuti seminar kampus}`).

### 4.3 Redesain Blok Tanda Tangan (2 Tingkat)
- Menghapus label dan nilai `NIM`, `NIP`, dan `NIK`.
- **Tingkat 1 (Kanan Atas)**:
  ```latex
  \hfill
  \begin{minipage}{0.40\textwidth}
  \centering
  Mahasiswa,\\[1.3cm]
  \textbf{{nama_mahasiswa}}
  \end{minipage}
  ```
- **Tingkat 2 (Tengah)**:
  ```latex
  \vspace{0.2cm}
  \begin{center}
  Mengetahui,
  \end{center}
  \vspace{0.1cm}
  ```
- **Tingkat 3 (Kiri & Kanan Bawah)**:
  ```latex
  \noindent
  \begin{minipage}[t]{0.45\textwidth}
  \centering
  Dosen Pembimbing,\\[1.3cm]
  \textbf{{nama_dosen}}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.45\textwidth}
  \centering
  Pembimbing Lapangan,\\[1.3cm]
  \textbf{{nama_lapangan}}
  \end{minipage}
  ```
- Jika nama pembimbing belum diisi, otomatis menampilkan garis titik-titik `....................................`.
- Total tinggi blok ~3.2cm, menjamin aturan ketat: **1 minggu = tepat 1 halaman A4**.

---

## 5. Integrasi Setup Wizard CLI & Web UI

### 5.1 Interactive CLI Setup Wizard (`main.py`)
Saat dijalankan jika `config.yaml` belum ada:
1. Meminta Nama, NIM, Program Studi, Nama Mitra.
2. Meminta **Tanggal Mulai Magang** (default: `2026-07-01`).
3. Meminta **Tanggal Selesai Magang** (default: `2026-12-31`).
4. Meminta **Pilihan Jadwal Kerja**:
   - `1`: 5 Hari Kerja (Senin–Jumat)
   - `2`: 6 Hari Kerja (Senin–Sabtu) [default]
5. Meminta Nama & NIP Dosen serta Nama & NIK Mentor.
6. Menyimpan hasil ke `config.yaml`.

### 5.2 Antarmuka Web Dashboard (`web/`)
1. **Modal Profil / Pengaturan**:
   - Input date picker `Tanggal Mulai` dan `Tanggal Selesai`.
   - Pilihan jadwal: Radio button `Senin–Jumat (5 Hari)` dan `Senin–Sabtu (6 Hari)`.
   - Simpan langsung memperbarui `config.yaml` dan me-refresh kalender di peramban web.
2. **Modal Edit Hari (Status Kehadiran)**:
   - Dropdown pilihan: `Hadir`, `Izin`, `Sakit`, `Cuti`, `Libur Nasional`.
   - Ketika dipilih status non-hadir:
     - Jam masuk & jam pulang otomatis diset `-` (disabled).
     - Pratinjau teks berwarna merah dengan label `[STATUS]`.
     - Tombol Formalize dan Saran Kegiatan disembunyikan/disesuaikan.
3. **Kartu Bento Mingguan**:
   - Baris hari Sabtu disembunyikan otomatis jika jadwal 5 hari aktif.
   - Badge status merah untuk hari dengan status izin/sakit/cuti/libur.

---

## 6. Rencana Pengujian & Verifikasi
1. **Unit Tests Kalender Dinamis**:
   - Uji rentang tanggal kustom (misal: 15 Agustus – 15 November).
   - Uji perbedaan jadwal 5 hari vs 6 hari (pastikan hari Sabtu tidak muncul pada jadwal 5 hari).
   - Uji pembagian bundel bulanan dinamis.
2. **Unit Tests LaTeX Builder & Rendering**:
   - Uji struktur header simetris 1 logo di kiri.
   - Uji blok tanda tangan bertingkat baru (Mahasiswa di kanan, Mengetahui di tengah, Dosen di kiri, Mentor di kanan).
   - Verifikasi bahwa string `NIM`, `NIP`, dan `NIK` tidak lagi muncul di blok tanda tangan.
   - Verifikasi kehadiran `\usepackage{xcolor}` dan output `\textcolor{red}{...}` untuk status Izin/Sakit/Cuti/Libur.
   - Verifikasi kepatuhan anggaran tinggi halaman (1 minggu = 1 halaman A4).
3. **API & Web UI Tests**:
   - Uji `POST /api/save-day` dengan payload status khusus (`{"date": "...", "status": "izin", "kegiatan": "..."}`).
   - Uji `GET /api/calendar` mengembalikan hari aktif sesuai konfigurasi 5 atau 6 hari.
   - Uji kompilasi PDF end-to-end melalui CLI dan REST endpoint.
