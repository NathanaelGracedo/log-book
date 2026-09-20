# Log Book Otomatis Magang Industri Polinema (JTI)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LaTeX: XeLaTeX](https://img.shields.io/badge/LaTeX-XeLaTeX-green.svg)](https://www.tug.org/xetex/)

Aplikasi otomatisasi pengisian dan pembuatan berkas PDF **Log Book Kegiatan Program Magang Industri** untuk mahasiswa Jurusan Teknologi Informasi (JTI) Politeknik Negeri Malang. Dilengkapi dengan antarmuka **CLI** dan **Web UI Dashboard** modern.

---

## ✨ Fitur Utama

1. **Format Resmi Presisi Tinggi (XeLaTeX)**:
   - Layout kop surat resmi simetris dengan logo Polinema.
   - Mengikuti kalender resmi periode magang (1 Juli 2026 s/d 31 Desember 2026).
   - Kalibrasi layout ketat: **Tepat 1 minggu = 1 lembar A4**.
   - Jadwal kerja: Senin–Jumat (08.00–16.00) dan Sabtu (08.00–14.00), Minggu libur.
2. **Ekspansi Narasi Formal Otomatis**:
   - Mengubah catatan singkat/poin-poin harian menjadi kalimat laporan formal berbahasa Indonesia yang rapi.
3. **Engine Kurikulum IT 158 Hari & Batch Auto-Fill**:
   - Menyediakan 158 template kegiatan software engineering realistis dari fase onboarding hingga serah terima proyek.
   - Fitur 1-klik untuk melengkapi hari-hari yang kosong secara otomatis.
4. **Modern Bento Grid Web Dashboard**:
   - Zero-npm (Vanilla HTML5/CSS/JS + FastAPI).
   - Tampilan visual status mingguan dan harian dengan indikator progres real-time.
   - Pratinjau langsung berkas PDF di dalam browser.
   - Dukungan tema otomatis (Terang / Gelap).
5. **Kesiapan Berbagi (GitHub Ready)**:
   - Pemisahan total antara data pribadi dan template publik (`config.example.yaml`).
   - Sistem pemeriksaan lingkungan otomatis (*Doctor Pre-flight Check*) untuk binary XeLaTeX.

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

### 3. Konfigurasi Profil Mahasiswa

Salin template konfigurasi dan sesuaikan data diri serta tempat magang Anda:

```bash
cp config.example.yaml config.yaml
```

Buka `config.yaml` dan sesuaikan:
- Nama Mahasiswa, NIM, Program Studi, dan Nama Mitra Industri.
- Nama & NIP Dosen Pembimbing Polinema.
- Nama & NIK/ID Pembimbing Lapangan / Mentor Industri.

---

## 🖥️ Penggunaan Web UI Dashboard

Jalankan server web lokal:

```bash
python3 main.py --ui
```

Buka peramban web di `http://127.0.0.1:8000`. Dari dashboard Anda dapat:
- Melihat ringkasan progres 158 hari magang.
- Mengedit catatan kegiatan harian secara visual.
- Menggunakan tombol **⚡ Formalize Narasi** untuk merapikan teks kegiatan.
- Menekan tombol **⚡ Auto-Fill Hari Kosong** untuk mengisi hari aktif yang belum terisi.
- Mengompilasi dan melihat pratinjau berkas PDF per bulan atau dokumen kumulatif secara langsung.

---

## ⌨️ Penggunaan Melalui CLI

Anda juga dapat menggunakan baris perintah langsung:

```bash
# Generate semua 6 berkas bulanan + 1 berkas kumulatif
python3 main.py --all

# Generate hanya bulan tertentu (contoh: Bulan ke-1 / Juli)
python3 main.py -m 1

# Generate hanya berkas PDF kumulatif lengkap (Juli - Desember)
python3 main.py --cumulative-only

# Periksa tanggal aktif yang belum memiliki catatan (tanpa kompilasi PDF)
python3 main.py --check-only

# Mode non-interaktif (berguna untuk skrip / CI)
python3 main.py --all --non-interactive
```

Berkas PDF hasil kompilasi akan tersimpan di direktori `output/`:
- `Logbook_01_Juli_2026.pdf` s/d `Logbook_06_Desember_2026.pdf`
- `Logbook_Lengkap_Juli_Desember_2026.pdf`

---

## 🧪 Pengujian Otomatis

Jalankan seluruh rangkaian tes unit dan integrasi end-to-end:

```bash
python3 -m unittest discover tests
```

---

## 📄 Lisensi

Proyek ini didistribusikan di bawah lisensi terbuka [MIT](LICENSE). Silakan gunakan, modifikasi, dan bagikan kepada rekan-rekan mahasiswa lainnya.
