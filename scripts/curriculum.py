# scripts/curriculum.py
"""
Curriculum Activity Generator for PT Naraya Telematika Internship.
Provides 158 structured, realistic software engineering and IT operational
tasks spanning 6 monthly phases (July - December 2026).
"""

import datetime
from pathlib import Path
from typing import Tuple
import yaml
from scripts.calendar_utils import get_internship_calendar, get_yaml_filename_for_date
from scripts.data_manager import load_all_notes, save_note_to_month, init_data_files

CURRICULUM_PHASES = [
    # Bulan 1: Onboarding, Setup Lingkungan, Arsitektur & Autentikasi Dasar
    [
        "Onboarding magang industri, pengenalan SOP perusahaan, dan koordinasi dengan tim rekayasa perangkat lunak.",
        "Setup workstation pengembang, konfigurasi runtime Docker, dan verifikasi kredensial repositori Git.",
        "Mempelajari arsitektur sistem backend, konvensi penamaan kode sumber, dan dokumentasi API internal.",
        "Eksplorasi skema basis data PostgreSQL modul otentikasi dan manajemen pengguna.",
        "Mengikuti sprint planning mingguan dan pembagian tiket backlog pengembangan fitur.",
        "Implementasi controller otentikasi JWT dan pembuatan payload access token.",
        "Pengembangan validasi form login dan sanitasi input keamanan payload request.",
        "Pengujian fungsional endpoint otentikasi menggunakan Postman dan dokumentasi respon HTTP.",
        "Debugging penanganan token kadaluarsa pada middleware verifikasi otorisasi pengguna.",
        "Dokumentasi alur otentikasi pada wiki teknis repositori pengembang.",
        "Koordinasi teknis dengan pembimbing lapangan mengenai struktur entitas data pengguna.",
        "Implementasi modul CRUD manajemen data profil pengguna pada layer repositori.",
        "Pengembangan logic filter dan pagination data tabel pengguna pada query database.",
        "Penulisan unit test untuk service layer modul manajemen pengguna.",
        "Code review bersama pembimbing lapangan untuk merge request fitur manajemen profil.",
        "Perbaikan feedback hasil review kode dan refactoring helper formatting tanggal.",
        "Meeting evaluasi sprint mingguan dan pemaparan capaian pengerjaan tiket.",
        "Mempelajari spesifikasi antrian pesan untuk asynchronous logging pada transaksi sistem.",
        "Instalasi dan konfigurasi message broker lokal untuk modul event tracking.",
        "Implementasi event producer untuk mencatat log aktivitas pengguna ke antrian.",
        "Implementasi event consumer worker untuk persistensi riwayat aktivitas ke database.",
        "Pengujian performa antrian pesan saat menerima request dalam jumlah bertahap.",
        "Penyusunan panduan deployment lokal dan konfigurasi environment worker service.",
        "Mengikuti sprint review mingguan dan demo fungsionalitas worker logging.",
        "Penyusunan modul pelaporan data pengguna terdaftar ke format spreadsheet.",
        "Optimasi query agregasi database untuk mempercepat response time laporan pengguna.",
        "Verifikasi indeks tabel database dan analisis query explain plan bersama senior backend engineer."
    ],
    # Bulan 2: Pengembangan Fitur Transaksi & API Master Data
    [
        "Evaluasi awal bulan bersama pembimbing lapangan dan perencanaan roadmap modul transaksi.",
        "Analisis spesifikasi kebutuhan sistem untuk modul pencatatan transaksi layanan.",
        "Perancangan Entity-Relationship Diagram (ERD) dan relasi foreign key tabel transaksi.",
        "Pembuatan migration file database untuk tabel transaksi dan tabel rincian transaksi.",
        "Implementasi layer data access object (DAO) untuk manipulasi data transaksi.",
        "Pengembangan endpoint RESTful API untuk pembuatan transaksi baru.",
        "Implementasi validasi bisnis logic: pengecekan ketersediaan kuota dan saldo akun.",
        "Pengujian skenario kegagalan transaksi menggunakan mock data pada unit test.",
        "Meeting koordinasi tim backend mengenai penanganan transaksi konkuren (database locking).",
        "Implementasi transaksi database ACID (commit & rollback) untuk menjaga integritas data.",
        "Dokumentasi spesifikasi OpenAPI/Swagger untuk seluruh endpoint modul transaksi.",
        "Code review berkala modul transaksi bersama tech lead dan pembimbing lapangan.",
        "Perbaikan validasi sanitasi input untuk mencegah celah keamanan SQL injection.",
        "Pengembangan endpoint pencarian dan filter riwayat transaksi berdasarkan tanggal.",
        "Implementasi caching query transaksi menggunakan Redis untuk mereduksi beban database.",
        "Pengujian kecepatan response time endpoint dengan dan tanpa mekanisme caching.",
        "Meeting mingguan tim rekayasa perangkat lunak dan sinkronisasi dependensi modul.",
        "Implementasi middleware rate limiter untuk membatasi lonjakan request pada endpoint publik.",
        "Penanganan edge cases error respon dan standardisasi format JSON exception handler.",
        "Penulisan integration test end-to-end untuk alur pembuatan transaksi hingga selesai.",
        "Investigasi bug laporan transaksi duplikat dan perbaikan race condition pada worker.",
        "Refactoring struktur kode controller dan pemisahan logic ke dalam business service terpisah.",
        "Meeting review sprint bulanan dan presentasi stabilitas modul transaksi.",
        "Persiapan migrasi skema database ke server staging untuk pengujian internal tim QA.",
        "Membantu verifikasi data hasil migrasi dan validasi integritas relasi tabel di staging.",
        "Penyusunan catatan rilis (release notes) versi sprint untuk modul transaksi."
    ],
    # Bulan 3: Optimasi Sistem, Asynchronous Tasks, dan Integrasi Modul
    [
        "Briefing awal bulan mengenai target optimasi performa dan integrasi modul antarmuka.",
        "Analisis log pemantauan performa server untuk mengidentifikasi bottleneck endpoint lambat.",
        "Optimasi query relasional tabel transaksi menggunakan strategi composite indexing.",
        "Pengurangan waktu eksekusi query agregasi bulanan hingga mencapai target latensi rendah.",
        "Implementasi scheduler task untuk otomasi kalkulasi ringkasan transaksi harian.",
        "Pengujian cron job scheduler pada environment development dan verifikasi log eksekusi.",
        "Implementasi mekanisme notifikasi email otomatis saat transaksi berhasil diproses.",
        "Konfigurasi template email responsif menggunakan engine rendering HTML server-side.",
        "Meeting mingguan koordinasi integrasi endpoint backend dengan tim frontend web.",
        "Penyelarasan kontrak data JSON antara client frontend dan API server backend.",
        "Pemberian dukungan teknis kepada tim frontend dalam integrasi modul autentikasi.",
        "Debugging masalah Cross-Origin Resource Sharing (CORS) pada komunikasi client-server.",
        "Implementasi webhook listener untuk menerima konfirmasi status pembayaran dari mitra.",
        "Verifikasi signature keamanan webhook untuk memastikan integritas payload kiriman mitra.",
        "Pengujian simulasi penerimaan webhook menggunakan webhook tester dan mocking tools.",
        "Code review bersama pembimbing lapangan untuk merge request integrasi webhook.",
        "Meeting mingguan evaluasi sprint dan pembahasan backlog fitur analitik laporan.",
        "Perancangan modul analitik performa penjualan dan visualisasi metrik data.",
        "Implementasi fungsi agregasi data statistik mingguan dan bulanan pada backend.",
        "Pengujian akurasi perhitungan metrik agregasi terhadap data transaksi riil di database.",
        "Pembersihan dependensi pustaka yang tidak terpakai untuk memperkecil ukuran container.",
        "Pembaruan dokumentasi arsitektur sistem dengan menambahkan diagram alur webhook.",
        "Meeting bulanan dan demo fitur analitik transaksi kepada tim produk Naraya.",
        "Pengujian regresi menyeluruh untuk memastikan integrasi webhook tidak mengganggu modul lama.",
        "Audit keamanan kode sumber menggunakan tools Static Application Security Testing (SAST).",
        "Perbaikan temuan audit keamanan terkait eksposur header HTTP sensitif."
    ],
    # Bulan 4: Penguatan Keamanan, Modul Pelaporan, dan Export Data
    [
        "Perencanaan sprint bulan keempat berfokus pada penguatan keamanan dan modul pelaporan.",
        "Implementasi kebijakan Content Security Policy (CSP) dan proteksi serangan CSRF.",
        "Pembaruan enkripsi password pengguna menggunakan algoritma hashing bcrypt terbaru.",
        "Penetration testing internal terhadap endpoint sensitif modul autentikasi dan profil.",
        "Meeting mingguan pembahasan format ekspor laporan keuangan dan operasional.",
        "Implementasi generator dokumen spreadsheet Excel menggunakan pustaka openpyxl.",
        "Styling format tabel laporan Excel meliputi header, border, dan formula akumulasi total.",
        "Pengujian kecepatan ekspor dokumen untuk dataset berukuran ribuan baris transaksi.",
        "Implementasi generator berkas PDF laporan bulanan resmi menggunakan formatting rapi.",
        "Konfigurasi watermark dan identitas institusi pada dokumen PDF hasil generate.",
        "Pengujian download berkas PDF dan verifikasi kesesuaian layout pada berbagai viewer.",
        "Code review modul pelaporan bersama pembimbing lapangan dan penyesuaian margin dokumen.",
        "Meeting koordinasi tim mengenai standarisasi audit trail aktivitas pengubah data.",
        "Implementasi tabel riwayat audit trail (siapa, kapan, dan field apa yang diubah).",
        "Pengembangan trigger database atau entity listener untuk otomatisasi pencatatan audit log.",
        "Pengujian keandalan audit trail saat terjadi pembatalan (rollback) transaksi.",
        "Meeting mingguan evaluasi sprint dan pembagian tugas perbaikan bug minor.",
        "Investigasi laporan issue pengguna terkait kegagalan unduh file laporan berukuran besar.",
        "Implementasi streaming response download file untuk menghemat konsumsi memori server.",
        "Verifikasi performa streaming download dan pengujian load test serentak.",
        "Refactoring kode generator dokumen agar reusable untuk berbagai jenis laporan.",
        "Penulisan panduan konfigurasi variabel environment untuk service pelaporan.",
        "Meeting bulanan pemaparan progres modul pelaporan dan keamanan sistem.",
        "Pembaruan skema dokumentasi API dengan menambahkan rincian parameter query ekspor.",
        "Uji kompatibilitas unduhan file laporan pada sistem operasi Linux, Windows, dan macOS.",
        "Backup berkala snapshot database staging dan verifikasi prosedur pemulihan data (restore).",
        "Evaluasi kinerja bulanan bersama pembimbing lapangan dan arahan fase berikutnya."
    ],
    # Bulan 5: Otomasi CI/CD, Containerization, dan Pengujian Skala Besar
    [
        "Briefing awal bulan mengenai standardisasi pipeline deployment dan automated testing.",
        "Penulisan skrip otomasi pipeline CI/CD menggunakan GitHub Actions / GitLab CI.",
        "Konfigurasi tahapan pipeline: linting kode, static code analysis, dan unit test otomatis.",
        "Optimasi caching layer pada Dockerfile multi-stage build untuk mempercepat build image.",
        "Meeting mingguan koordinasi tim DevOps dan review konfigurasi container environment.",
        "Implementasi health check endpoint (/health) untuk pemantauan ketersediaan service.",
        "Konfigurasi monitoring utilisasi CPU, memori, dan latency endpoint menggunakan Prometheus.",
        "Pembuatan dashboard visualisasi metrik server pada Grafana bersama tim infrastruktur.",
        "Pengujian simulasi kegagalan container dan verifikasi mekanisme auto-restart service.",
        "Meeting sinkronisasi mingguan dan pembahasan persiapan pengujian beban (load testing).",
        "Penyusunan skenario pengujian beban menggunakan tools k6 / Apache JMeter.",
        "Eksekusi stress testing pada endpoint transaksi untuk mencari batas kapasitas server.",
        "Analisis grafik throughput dan identifikasi bottleneck pada koneksi database connection pool.",
        "Tuning parameter connection pool PostgreSQL untuk meningkatkan kapasitas concurrent users.",
        "Code review berkala skrip CI/CD dan penyesuaian aturan proteksi branch repository.",
        "Verifikasi pipeline CI/CD berjalan sukses secara otomatis pada setiap pull request.",
        "Meeting evaluasi mingguan dan review stabilitas server staging pasca tuning database.",
        "Implementasi sistem rotasi berkas log server untuk mencegah kepenuhan kapasitas disk.",
        "Pembersihan docker image dan volume yang tidak digunakan pada server deployment.",
        "Pembaruan skrip migrasi database agar dapat berjalan otomatis saat proses deployment.",
        "Pengujian alur rollback deployment otomatis ketika terdeteksi kegagalan build.",
        "Dokumentasi standar operasional prosedur (SOP) deployment dan pemeliharaan server.",
        "Meeting bulanan mengenai evaluasi performa sistem dan kesiapan memasuki fase final.",
        "Audit kelayakan release staging bersama tech lead dan pembimbing industri.",
        "Penyusunan daftar perbaikan bug minor menjelang User Acceptance Testing (UAT)."
    ],
    # Bulan 6: UAT, Stabilisasi, Dokumentasi Akhir, dan Serah Terima Sistem
    [
        "Kick-off fase final magang: perencanaan User Acceptance Testing (UAT) dan dokumentasi akhir.",
        "Penyusunan dokumen skenario pengujian UAT bersama tim produk dan perwakilan pengguna.",
        "Pendampingan sesi pengujian UAT modul manajemen pengguna dan pencatatan transaksi.",
        "Pencatatan feedback, temuan anomali, dan permintaan penyesuaian minor dari hasil UAT.",
        "Meeting mingguan pembahasan prioritas tiket perbaikan berdasarkan hasil sesi UAT.",
        "Perbaikan validasi form input berdasarkan masukan kemudahan pengguna (user-friendly).",
        "Penyesuaian pesan notifikasi error agar lebih informatif dan mudah dipahami pengguna awam.",
        "Pengujian ulang verifikasi perbaikan issue UAT pada lingkungan staging.",
        "Penyelesaian seluruh tiket perbaikan prioritas tinggi dengan status lulus verifikasi.",
        "Code review final bersama seluruh tim pengembang sebelum merge ke branch release utama.",
        "Finalisasi standarisasi kode sumber dan pembersihan file artefak pengembangan sementara.",
        "Penyusunan dokumentasi teknis komprehensif: arsitektur sistem, skema database, dan API contract.",
        "Meeting mingguan evaluasi kesiapan rilis produksi dan verifikasi checklist deployment.",
        "Penyusunan panduan instalasi sistem bagi administrator dan panduan penggunaan bagi user.",
        "Pembuatan video tutorial singkat mengenai alur operasional fitur utama aplikasi.",
        "Presentasi hasil pengembangan sistem kepada tim manajemen PT Naraya Telematika.",
        "Diskusi tanya jawab teknis dan penerimaan apresiasi serta evaluasi dari para stakeholder.",
        "Penyusunan laporan akhir kegiatan magang industri dan pengumpulan data rekapitulasi.",
        "Rekapitulasi seluruh log book kegiatan harian dan pencocokan dengan capaian kurikulum kampus.",
        "Kompilasi berkas PDF resmi log book magang Polinema untuk periode Juli s/d Desember 2026.",
        "Pemeriksaan kelengkapan dokumen pengesahan log book bersama dosen pembimbing.",
        "Konsultasi draf laporan magang industri bersama dosen pembimbing Polinema.",
        "Revisi draf laporan akhir sesuai masukan dan catatan akademik dari dosen pembimbing.",
        "Penyusunan slide presentasi seminar magang industri di Jurusan Teknologi Informasi Polinema.",
        "Gladi bersih pemaparan materi seminar magang dan persiapan demonstrasi program aplikasi.",
        "Serah terima resmi artefak kode sumber, dokumentasi teknis, dan akun kepada pihak industri.",
        "Penutupan program magang industri di PT Naraya Telematika dan evaluasi akhir pembimbing lapangan."
    ]
]

def get_curriculum_task(date_val: datetime.date, day_index: int) -> str:
    """Returns a realistic IT task for the given date and chronological day index (0..157)."""
    month = date_val.month
    phase_idx = max(0, min(5, month - 7))
    phase_tasks = CURRICULUM_PHASES[phase_idx]
    task_idx = day_index % len(phase_tasks)
    return phase_tasks[task_idx]

def batch_autofill_notes(overwrite_existing: bool = False, data_dir: str = "data") -> Tuple[int, int]:
    """
    Fills empty days in all 6 monthly YAML files with realistic IT internship tasks.
    If overwrite_existing is False, existing manual notes are preserved.
    Returns (filled_count, total_empty_before_run).
    """
    init_data_files(data_dir)
    weeks = get_internship_calendar()
    existing_notes = load_all_notes(data_dir)
    
    day_counter = 0
    filled_count = 0
    empty_count = 0
    
    for w in weeks:
        for day in w["days"]:
            d = day["date"]
            d_str = day["date_str"]
            is_empty = (d_str not in existing_notes) or not str(existing_notes[d_str]).strip()
            
            if is_empty:
                empty_count += 1
                task = get_curriculum_task(d, day_counter)
                save_note_to_month(d, task, data_dir)
                filled_count += 1
            elif overwrite_existing:
                task = get_curriculum_task(d, day_counter)
                save_note_to_month(d, task, data_dir)
                filled_count += 1
            
            day_counter += 1
            
    return filled_count, empty_count
