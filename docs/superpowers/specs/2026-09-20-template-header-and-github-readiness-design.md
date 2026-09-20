# Desain Perbaikan Header LaTeX & Standarisasi Repositori GitHub

## 1. Ringkasan & Tujuan
Revisi template kop surat LaTeX dan persiapan standarisasi repositori publik GitHub untuk proyek **Log Book Otomatis Magang Industri Polinema (JTI)**.

Tujuan utama:
1. **Perbaikan Layout Kop Surat**: Menghapus duplikasi logo Polinema di sisi kanan sehingga hanya tampil 1 logo di kiri, dengan posisi blok teks instansi tetap terpusat dan 100% simetris.
2. **Kesiapan Kloning Rekan Mahasiswa (GitHub Readiness)**: Memastikan rekan mahasiswa JTI Polinema dari berbagai tempat magang lain dapat melakukan `git clone` dan langsung menjalankan platform ini (baik via CLI maupun Web UI) tanpa kendala konfigurasi, tanpa kebocoran data pribadi pembuat, dan tanpa memerlukan dependensi AI agent.

---

## 2. Spesifikasi Perbaikan Header LaTeX

### 2.1 Analisis Masalah
Pada implementasi sebelumnya, kop surat memuat dua logo (kiri dan kanan), yang keduanya mengekstrak aset logo Polinema sehingga terjadi duplikasi visual.

### 2.2 Desain Layout Simetris Baru
Menggunakan sistem grid 3 minipage pada `scripts/latex_builder.py`:
- **Minipage Kiri (`0.15\textwidth`)**:
  - Berisi logo resmi Polinema (`assets/polinema.png`), tinggi diatur `1.8cm`, perataan tengah (`\centering`).
- **Minipage Tengah (`0.70\textwidth`)**:
  - Berisi teks resmi instansi:
    - *KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI*
    - *POLITEKNIK NEGERI MALANG*
    - *JURUSAN TEKNOLOGI INFORMASI*
    - Alamat, Telepon, Faksimile, Laman.
  - Perataan tengah (`\centering`).
- **Minipage Kanan (`0.15\textwidth`)**:
  - Kolom kosong penyeimbang matematis (*counterweight* `\hfill` / `~`).
  - Menjamin sumbu tengah teks instansi berada tepat di titik tengah kertas A4 (tidak bergeser ke kanan).
- **Garis Pembatas Kop**:
  - Dua garis horizontal (`\hrule height 1.2pt` dan `\hrule height 0.5pt`) tetap dipertahankan dengan jarak presisi.

---

## 3. Standarisasi Repositori GitHub untuk Pengguna Lain

### 3.1 Sanitasi & Pemisahan Data Pribadi
1. **`config.example.yaml`**:
   - Dibuat sebagai acuan konfigurasi publik dengan instruksi pengisian:
     ```yaml
     mahasiswa:
       nama: "Nama Lengkap Mahasiswa"
       nim: "XXXXXXXXXX"
       prodi: "Sarjana Terapan Teknik Informatika" # atau D4 Sistem Informasi Bisnis
       mitra: "Nama Perusahaan / Tempat Magang"

     pembimbing:
       dosen:
         nama: "Nama Dosen Pembimbing, S.Kom., M.Kom."
         nip: "198XXXXXXXXXXXX"
       lapangan:
         nama: "Nama Pembimbing Lapangan / Mentor"
         nik: "NIK / ID Karyawan"

     pengaturan:
       jam_kerja:
         senin_jumat:
           masuk: "08.00"
           pulang: "16.00"
         sabtu:
           masuk: "08.00"
           pulang: "14.00"
     ```
2. **Pembaruan `.gitignore`**:
   - Mengabaikan `config.yaml` agar identitas pribadi pengembang asli tidak terunggah ke publik.
   - Mengabaikan `output/` (*.pdf hasil kompilasi pribadi).
   - Mengabaikan berkas sementara kompilasi LaTeX (`*.aux`, `*.log`, `*.out`, `*.toc`).
   - Mengabaikan `data/*.yaml` pribadi pengembang (hanya menyertakan starter data atau panduan di `data/`).
3. **Auto-Bootstrap Konfigurasi**:
   - Jika `main.py` dijalankan dan `config.yaml` belum ada, sistem secara otomatis menyalin `config.example.yaml` menjadi `config.yaml` dan mencetak instruksi ramah di terminal.

### 3.2 Pemeriksaan Lingkungan Otomatis (Pre-flight Check / Doctor)
Pada awal eksekusi `main.py`:
- Memeriksa keberadaan binary `xelatex` di sistem pengguna (`shutil.which("xelatex")`).
- Jika `xelatex` tidak ditemukan, tampilkan pesan informatif ramah pemula beserta perintah instalasinya:
  - Ubuntu / Debian / Linux Mint: `sudo apt install texlive-xetex texlive-fonts-recommended`
  - Arch Linux: `sudo pacman -S texlive-bin texlive-core`
  - Fedora: `sudo dnf install texlive-xetex texlive-collection-fontsrecommended`
  - macOS: `brew install --cask mactex-no-gui`
  - Windows: Pasang [MiKTeX](https://miktex.org/download)

### 3.3 Dokumentasi Komprehensif `README.md`
Memuat panduan lengkap:
1. **Deskripsi Singkat**: Otomatisasi Log Book Magang JTI Polinema dengan dukungan CLI dan Web UI interaktif.
2. **Fitur Utama**:
   - Layout resmi presisi 1 minggu per lembar A4.
   - Generator narasi kegiatan IT formal dari poin singkat.
   - Fitur Batch Auto-Fill untuk melengkapi hari-hari kosong.
   - Web UI modern berbasis FastAPI.
3. **Quickstart 3 Menit**:
   ```bash
   git clone <repo-url>
   cd log-book
   pip install -r requirements.txt
   cp config.example.yaml config.yaml   # Edit data diri & mitra
   python3 main.py --ui                 # Buka dashboard di browser
   ```
4. **Cara Penggunaan CLI**:
   - `python3 main.py --all` : Generate seluruh bulan + kumulatif.
   - `python3 main.py -m 1` : Generate log book bulan ke-1 (Juli).
   - `python3 main.py --check-only` : Cek tanggal kosong.
5. **Lisensi**:
   - Lisensi sumber terbuka MIT (`LICENSE`).

---

## 4. Rencana Pengujian & Verifikasi
1. **Visual Verification**:
   - Jalankan kompilasi halaman minggu pertama (`Logbook_01_Juli_2026.pdf`).
   - Konversi halaman pertama ke gambar PNG atau periksa pratinjau untuk memastikan hanya ada 1 logo Polinema di kiri dan teks kop terpusat simetris.
2. **Bootstrap Verification**:
   - Simulasikan kondisi pengguna baru (hapus sementara `config.yaml` di lingkungan tes) dan jalankan `main.py` untuk memastikan pesan peringatan dan pembuatan otomatis `config.yaml` berjalan mulus.
3. **Git Cleanliness**:
   - Periksa `git status` untuk memastikan tidak ada berkas PDF, log LaTeX, atau berkas konfigurasi pribadi yang masuk ke area staging.
