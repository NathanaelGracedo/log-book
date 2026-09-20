# Log Book Otomatis Magang Industri Polinema (JTI)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LaTeX: XeLaTeX](https://img.shields.io/badge/LaTeX-XeLaTeX-green.svg)](https://www.tug.org/xetex/)

Aplikasi otomatisasi pengisian dan pembuatan berkas PDF **Log Book Kegiatan Program Magang Industri** untuk mahasiswa Jurusan Teknologi Informasi (JTI) Politeknik Negeri Malang. Dilengkapi dengan antarmuka **CLI** interaktif dan **Web UI Dashboard** modern.

---

## ✨ Fitur Utama

1. **Format Resmi Presisi Tinggi (XeLaTeX) & Redesain Tanda Tangan 2-Tier**:
   - Layout kop surat resmi simetris dengan logo Polinema.
   - **Tata letak tanda tangan 2-tier**: Mahasiswa pada tingkat atas (kanan), diikuti *Mengetahui* dengan Dosen Pembimbing Polinema dan Pembimbing Lapangan / Mentor Industri pada tingkat bawah yang sejajar dan proporsional.
   - Penghapusan label redundan `NIM.`, `NIP.`, dan `NIK.` pada blok tanda tangan sesuai format dokumen resmi.
   - Kalibrasi layout ketat: **Tepat 1 minggu = 1 lembar A4**.
2. **Periode Magang Dinamis & Jadwal Kerja Fleksibel**:
   - Rentang tanggal magang dinamis (`periode.tanggal_mulai` dan `periode.tanggal_selesai`), tidak terpaku pada rentang statis. Sistem otomatis menghitung bundle bulan dan penomoran minggu yang akurat.
   - Pilihan jadwal kerja (`pengaturan.hari_kerja`):
     - **5 Hari Kerja (`senin_jumat`)**: Senin–Jumat aktif (08.00–16.00), Sabtu & Minggu libur.
     - **6 Hari Kerja (`senin_sabtu`)**: Senin–Jumat (08.00–16.00) dan Sabtu (08.00–14.00), Minggu libur.
3. **Dukungan Status Kehadiran (Attendance Status)**:
   - Mendukung 5 pilihan status presensi: **Hadir**, **Izin**, **Sakit**, **Cuti**, dan **Libur Nasional**.
   - Pengaturan jam kerja otomatis: Status non-hadir otomatis mengisi jam datang dan pulang dengan tanda strip (`-`).
   - Penanda teks merah tebal otomatis pada berkas PDF untuk status non-hadir (misal: `\textcolor{red}{\textbf{[IZIN]:} ...}`).
4. **Interactive Setup Wizard (CLI & Web UI)**:
   - Panduan konfigurasi interaktif (`python3 main.py --init`) untuk pemula dalam menyiapkan data diri, mitra, periode tanggal, dan jadwal kerja.
   - Pengaturan konfigurasi langsung via antarmuka modal pada Web Dashboard.
5. **Ekspansi Narasi Formal Otomatis**:
   - Mengubah catatan singkat/poin-poin harian menjadi kalimat laporan formal berbahasa Indonesia yang rapi.
6. **Engine Kurikulum IT 158 Hari & Batch Auto-Fill**:
   - Menyediakan 158 template kegiatan software engineering realistis dari fase onboarding hingga serah terima proyek.
   - Fitur 1-klik untuk melengkapi hari-hari aktif yang kosong secara otomatis.
7. **Modern Bento Grid Web Dashboard**:
   - Zero-npm (Vanilla HTML5/CSS/JS + FastAPI).
   - Tampilan visual status mingguan dan harian dengan indikator progres real-time.
   - Modal edit kegiatan harian dengan dropdown pemilihan status kehadiran.
   - Pratinjau langsung berkas PDF di dalam browser dengan dukungan tema gelap/terang.

---

## 🚀 Quickstart (3 Menit)

### 1. Kloning Repositori & Pasang Dependensi

```bash
git clone https://github.com/username/log-book.git
cd log-book

# Pasang dependensi Python
pip install -r requirements.txt
```

### 2. Pasang XeLaTeX (Jika Belum Terpasang)

- **Ubuntu / Debian / Linux Mint:**
  ```bash
  sudo apt update && sudo apt install -y texlive-xetex texlive-fonts-recommended
  ```
- **Arch Linux / Manjaro:**
  ```bash
  sudo pacman -S texlive-bin texlive-core
  ```
- **Fedora:**
  ```bash
  sudo dnf install texlive-xetex texlive-collection-fontsrecommended
  ```
- **macOS:**
  ```bash
  brew install --cask mactex-no-gui
  ```
- **Windows:** Pasang [MiKTeX](https://miktex.org/download).

### 3. Konfigurasi Profil Mahasiswa & Periode

Anda dapat menggunakan **Setup Wizard Interaktif** (direkomendasikan) atau menyalin berkas konfigurasi secara manual:

#### Opsi A: Setup Wizard CLI (Rekomendasi)
```bash
python3 main.py --init
```
Wizard akan menuntun Anda mengisikan:
- Nama Mahasiswa, NIM, Program Studi, dan Tempat Magang.
- Tanggal mulai dan tanggal selesai periode magang (`YYYY-MM-DD`).
- Pilihan jadwal kerja: 5 hari (`senin_jumat`) atau 6 hari (`senin_sabtu`).
- Data Dosen Pembimbing (Nama & NIP) serta Pembimbing Lapangan (Nama & NIK/ID).

#### Opsi B: Konfigurasi Manual
```bash
cp config.example.yaml config.yaml
```
Buka dan sesuaikan `config.yaml`:
```yaml
mahasiswa:
  nama: "Nama Lengkap Mahasiswa"
  nim: "XXXXXXXXXX"
  prodi: "Sarjana Terapan Teknik Informatika"
  mitra: "Nama Perusahaan / Tempat Magang"

periode:
  tanggal_mulai: "2026-07-01"    # Tanggal mulai magang (YYYY-MM-DD)
  tanggal_selesai: "2026-12-31"  # Tanggal selesai magang (YYYY-MM-DD)

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
    nip: "198XXXXXXXXXXXXXXX"
  lapangan:
    nama: "Nama Pembimbing Lapangan / Mentor"
    nik: "NIK / ID Karyawan"
```

---

## 📋 Status Kehadiran (Attendance Status)

Sistem mendukung 5 jenis status kehadiran harian:
- **Hadir**: Menjalankan aktivitas kerja normal (jam masuk & pulang terisi sesuai konfigurasi jam kerja).
- **Izin**: Izin tidak masuk kerja (jam kerja otomatis `-`, teks kegiatan dicetak merah dengan prefiks `[IZIN]:`).
- **Sakit**: Sakit / istirahat medis (jam kerja otomatis `-`, teks kegiatan dicetak merah dengan prefiks `[SAKIT]:`).
- **Cuti**: Cuti magang (jam kerja otomatis `-`, teks kegiatan dicetak merah dengan prefiks `[CUTI]:`).
- **Libur Nasional**: Hari libur resmi atau dispensasi kampus (jam kerja otomatis `-`, teks kegiatan dicetak merah dengan prefiks `[LIBUR]:`).

Format penyimpanan pada berkas data bulanan (`data/bulan_XX_*.yaml`) mendukung dua format yang kompatibel:
```yaml
catatan:
  # Format teks langsung (otomatis berstatus 'hadir'):
  "2026-07-01": "onboarding magang industri dan pengenalan tim rekayasa perangkat lunak"

  # Format objek terstruktur dengan status khusus:
  "2026-07-02":
    status: "izin"
    kegiatan: "Izin menghadiri yudisium program studi di kampus"
```

---

## 🖥️ Penggunaan Web UI Dashboard

Jalankan server web lokal:

```bash
python3 main.py --ui
```

Buka peramban web di `http://127.0.0.1:8000`. Dari dashboard Anda dapat:
- Melihat ringkasan progres hari magang sesuai rentang periode aktif.
- Memilih status kehadiran (**Hadir**, **Izin**, **Sakit**, **Cuti**, **Libur Nasional**) pada dialog edit harian.
- Mengubah periode magang dan jadwal kerja langsung melalui modal **Settings / Pengaturan**.
- Menggunakan tombol **⚡ Formalize Narasi** untuk merapikan teks kegiatan.
- Menekan tombol **⚡ Auto-Fill Hari Kosong** untuk mengisi hari aktif yang belum terisi.
- Mengompilasi dan melihat pratinjau berkas PDF per bulan atau dokumen kumulatif secara langsung.

---

## ⌨️ Penggunaan Melalui CLI

Anda juga dapat menggunakan baris perintah langsung:

```bash
# Inisialisasi wizard konfigurasi interaktif
python3 main.py --init

# Generate semua berkas bulanan + 1 berkas kumulatif
python3 main.py --all

# Generate hanya bulan tertentu (contoh: Bulan ke-1)
python3 main.py -m 1

# Generate hanya berkas PDF kumulatif lengkap
python3 main.py --cumulative-only

# Periksa tanggal aktif yang belum memiliki catatan (tanpa kompilasi PDF)
python3 main.py --check-only

# Mode non-interaktif (berguna untuk skrip / CI)
python3 main.py --all --non-interactive
```

Berkas PDF hasil kompilasi akan tersimpan di direktori `output/`:
- `Logbook_01_Juli_2026.pdf` s/d berkas bulan terakhir
- `Logbook_Lengkap_Juli_Desember_2026.pdf` (atau rentang yang dikonfigurasi)

---

## 🧪 Pengujian Otomatis

Jalankan seluruh rangkaian tes unit dan integrasi end-to-end:

```bash
python3 -m unittest discover tests
```

---

## 📄 Lisensi

Proyek ini didistribusikan di bawah lisensi terbuka [MIT](LICENSE). Silakan gunakan, modifikasi, dan bagikan kepada rekan-rekan mahasiswa lainnya.
