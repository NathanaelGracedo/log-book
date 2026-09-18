# Log Book Web UI Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modern, zero-npm local Web UI dashboard (FastAPI + Vanilla HTML5/CSS/JS Bento Grid) that enables visual progress tracking, 1-click note formalization, batch auto-filling of empty days with realistic IT curriculum tasks, profile management, and live browser PDF preview for Polinema industrial internship logbooks.

**Architecture:** A lightweight FastAPI backend (`web/app.py`) interfaces with existing core modules (`calendar_utils`, `data_manager`, `narrative_expander`, `latex_builder`) and a new IT curriculum generator (`scripts/curriculum.py`). A zero-dependency single-page application (`web/static/`) serves an academic blue and dark-mode-ready Bento Grid UI using native Fetch API. CLI flag `python3 main.py --ui` launches the dashboard via Uvicorn.

**Tech Stack:** Python 3, FastAPI, Uvicorn, Pydantic, PyYAML, Vanilla HTML5, Modern CSS (CSS Tokens, Bento Grid, Dark Mode), Vanilla JavaScript (ES6+ Fetch API, reactive DOM state), XeLaTeX.

---

## Global Constraints

- **Python Runtime:** Python 3.10+ (tested on Python 3.14).
- **Backend Dependencies:** `fastapi`, `uvicorn`, `pydantic`, `httpx` (for test client), `pyyaml`.
- **Frontend Dependencies:** Zero Node.js / npm dependencies. Pure native HTML5, CSS3, and ES6+ JavaScript.
- **Internship Period:** Wednesday, July 1, 2026 to Thursday, December 31, 2026 (158 working days, 27 weeks).
- **Schedule Rules:** 6 working days per week (Monday–Saturday); Sunday is off / omitted.
- **Working Hours:** Monday–Friday 08.00–16.00, Saturday 08.00–14.00.
- **Color Tokens:** Academic Blue (`#2563EB`), Emerald Green (`#059669`), Amber Warning (`#D97706`), Dark Background (`#0F172A`), Light Background (`#F8FAFC`).
- **File Encoding:** UTF-8 throughout.
- **Testing Standard:** 100% test pass rate on `python3 -m unittest discover tests`.

---

## File Structure

```text
log-book/
├── requirements.txt             # Project dependencies (fastapi, uvicorn, etc.)
├── main.py                      # CLI entrypoint with --ui flag
├── scripts/
│   ├── calendar_utils.py        # Calendar partitioning (existing)
│   ├── data_manager.py          # YAML note storage (existing)
│   ├── narrative_expander.py    # Formal Indonesian sentence expansion (existing)
│   ├── latex_builder.py         # XeLaTeX document compiler (existing)
│   └── curriculum.py            # PT Naraya Telematika 158-day IT curriculum & batch autofill (new)
├── web/
│   ├── __init__.py              # Web package marker
│   ├── app.py                   # FastAPI application & REST endpoints
│   └── static/
│       ├── index.html           # SPA Dashboard HTML5 layout & modals
│       ├── styles.css           # Bento Grid CSS Design System & Dark Mode
│       └── app.js               # Reactive client state, API calls, DOM rendering
└── tests/
    ├── test_curriculum.py       # Unit tests for curriculum task generator
    ├── test_web_api.py          # API endpoint tests with FastAPI TestClient
    ├── test_web_pdf.py          # PDF generation & streaming endpoint tests
    └── test_cli_ui.py           # CLI --ui flag and startup tests
```

---

### Task 1: Dependencies & IT Curriculum Engine

**Files:**
- Create: `requirements.txt`
- Create: `scripts/curriculum.py`
- Test: `tests/test_curriculum.py`

**Interfaces:**
- Consumes: `scripts.calendar_utils.get_internship_calendar`, `scripts.data_manager.save_note_to_month`, `scripts.data_manager.load_all_notes`
- Produces: 
  - `get_curriculum_task(date_val: datetime.date, day_index: int) -> str`
  - `batch_autofill_notes(overwrite_existing: bool = False, data_dir: str = "data") -> tuple[int, int]` (returns `(filled_count, total_empty)`)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_curriculum.py
import unittest
import datetime
import tempfile
import os
import shutil
import yaml
from scripts.curriculum import get_curriculum_task, batch_autofill_notes
from scripts.calendar_utils import get_internship_calendar

class TestCurriculumEngine(unittest.TestCase):
    def test_curriculum_task_for_specific_dates(self):
        # Day 0 (2026-07-01) should be onboarding/orientation
        task_1 = get_curriculum_task(datetime.date(2026, 7, 1), 0)
        self.assertIn("onboarding", task_1.lower())
        self.assertTrue(len(task_1) > 10)

        # Day 157 (final day in Dec) should be final report / handover
        task_last = get_curriculum_task(datetime.date(2026, 12, 31), 157)
        self.assertTrue("laporan" in task_last.lower() or "evaluasi" in task_last.lower() or "serah terima" in task_last.lower())

    def test_batch_autofill_without_overwrite(self):
        tmp_dir = tempfile.mkdtemp(prefix="test_curriculum_")
        try:
            # Seed July with 1 existing note
            july_file = os.path.join(tmp_dir, "bulan_01_juli.yaml")
            os.makedirs(tmp_dir, exist_ok=True)
            with open(july_file, "w", encoding="utf-8") as f:
                yaml.dump({
                    "bulan": 7,
                    "tahun": 2026,
                    "catatan": {
                        "2026-07-01": "Catatan manual mahasiswa yang tidak boleh ditimpa"
                    }
                }, f)

            filled, total_missing = batch_autofill_notes(overwrite_existing=False, data_dir=tmp_dir)
            self.assertGreater(filled, 0)
            self.assertEqual(total_missing, 157)

            # Verify existing note was preserved
            with open(july_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self.assertEqual(data["catatan"]["2026-07-01"], "Catatan manual mahasiswa yang tidak boleh ditimpa")
            # Verify another date was auto-filled
            self.assertIn("2026-07-02", data["catatan"])
            self.assertTrue(len(data["catatan"]["2026-07-02"]) > 5)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_curriculum.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.curriculum'`

- [ ] **Step 3: Implement dependencies and curriculum generator**

Create `requirements.txt`:
```text
fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.0
pyyaml>=6.0.1
httpx>=0.27.0
```

Install dependencies:
```bash
python3 -m pip install --user -r requirements.txt
```

Create `scripts/curriculum.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_curriculum.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add requirements.txt scripts/curriculum.py tests/test_curriculum.py
git commit -m "feat: add dependencies and 158-day IT curriculum generator"
```

---

### Task 2: FastAPI Application & Data/Calendar REST Endpoints

**Files:**
- Create: `web/__init__.py`
- Create: `web/app.py`
- Test: `tests/test_web_api.py`

**Interfaces:**
- Consumes:
  - `scripts.calendar_utils.get_internship_calendar`
  - `scripts.calendar_utils.get_month_bundle_weeks`
  - `scripts.calendar_utils.INDONESIAN_MONTHS`
  - `scripts.data_manager.load_all_notes`
  - `scripts.data_manager.save_note_to_month`
  - `scripts.narrative_expander.expand_narrative`
  - `scripts.curriculum.batch_autofill_notes`
  - `main.load_config`
- Produces:
  - FastAPI app instance `web.app.app`
  - Endpoints: `GET /api/calendar`, `POST /api/save-day`, `POST /api/formalize`, `POST /api/batch-autofill`, `GET /api/config`, `POST /api/config`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_web_api.py
import unittest
from fastapi.testclient import TestClient
import tempfile
import os
import shutil
import yaml

class TestWebApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from web.app import app
        cls.client = TestClient(app)

    def test_get_calendar_structure(self):
        res = self.client.get("/api/calendar")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_days"], 158)
        self.assertIn("filled_days", data)
        self.assertIn("missing_days", data)
        self.assertIn("percentage", data)
        self.assertEqual(len(data["months"]), 6)
        
        month_1 = data["months"][0]
        self.assertEqual(month_1["month_index"], 1)
        self.assertEqual(month_1["name"], "Juli 2026")
        self.assertEqual(len(month_1["weeks"]), 5)

    def test_formalize_endpoint(self):
        res = self.client.post("/api/formalize", json={"note": "testing api auth postman"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("formalized", data)
        self.assertTrue(data["formalized"].endswith("."))
        self.assertTrue(data["formalized"][0].isupper())

    def test_save_day_endpoint(self):
        res = self.client.post("/api/save-day", json={"date": "2026-07-01", "note": "Onboarding dan pengenalan tim pengembang."})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_config_endpoints(self):
        # GET config
        res_get = self.client.get("/api/config")
        self.assertEqual(res_get.status_code, 200)
        cfg = res_get.json()
        self.assertIn("mahasiswa", cfg)
        self.assertIn("pembimbing", cfg)

        # POST config update (non-destructive)
        res_post = self.client.post("/api/config", json=cfg)
        self.assertEqual(res_post.status_code, 200)
        self.assertEqual(res_post.json()["status"], "ok")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'web'`

- [ ] **Step 3: Implement `web/__init__.py` and `web/app.py`**

Create `web/__init__.py`:
```python
# web/__init__.py
```

Create `web/app.py`:
```python
# web/app.py
"""
FastAPI Backend Application for Polinema Log Book Automation Dashboard.
Provides REST API endpoints for calendar monitoring, daily note CRUD,
narrative formalization, batch auto-filling, profile configuration,
and live PDF preview streaming.
"""

import os
import datetime
from pathlib import Path
from typing import Optional, Any, Dict
import yaml
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from scripts.calendar_utils import (
    get_internship_calendar,
    get_month_bundle_weeks,
    INDONESIAN_MONTHS,
    format_indonesian_date
)
from scripts.data_manager import (
    load_all_notes,
    save_note_to_month,
    init_data_files
)
from scripts.narrative_expander import expand_narrative
from scripts.curriculum import batch_autofill_notes
from main import load_config

app = FastAPI(title="Log Book Polinema Dashboard API", version="1.0.0")

# Request Schemas
class SaveDayRequest(BaseModel):
    date: str
    note: str

class FormalizeRequest(BaseModel):
    note: str

class BatchAutofillRequest(BaseModel):
    overwrite_existing: bool = False

# Ensure data directory is initialized
init_data_files("data")

@app.get("/api/calendar")
def get_calendar() -> Dict[str, Any]:
    """Returns the full 27-week internship calendar, partitioned into 6 monthly bundles."""
    notes_map = load_all_notes("data")
    all_weeks = get_internship_calendar()
    
    total_days = sum(len(w["days"]) for w in all_weeks)
    filled_days = 0
    
    # Enrich day dicts with note and is_filled status
    enriched_calendar = []
    for w in all_weeks:
        week_days = []
        for d in w["days"]:
            d_str = d["date_str"]
            note = notes_map.get(d_str, "")
            is_filled = bool(note and note.strip())
            if is_filled:
                filled_days += 1
            day_copy = dict(d)
            day_copy["note"] = note
            day_copy["is_filled"] = is_filled
            day_copy["date"] = d["date"].strftime("%Y-%m-%d")
            week_days.append(day_copy)
        enriched_calendar.append({
            "minggu_ke": w["minggu_ke"],
            "days": week_days
        })
        
    missing_days = total_days - filled_days
    percentage = round((filled_days / total_days * 100), 1) if total_days > 0 else 0.0
    
    # Group into 6 monthly bundles
    months_data = []
    month_week_ranges = {
        1: (1, 5, "Juli 2026"),
        2: (6, 9, "Agustus 2026"),
        3: (10, 14, "September 2026"),
        4: (15, 18, "Oktober 2026"),
        5: (19, 22, "November 2026"),
        6: (23, 27, "Desember 2026"),
    }
    
    for m_idx, (w_start, w_end, name) in month_week_ranges.items():
        bundle_weeks = [w for w in enriched_calendar if w_start <= w["minggu_ke"] <= w_end]
        b_total = sum(len(w["days"]) for w in bundle_weeks)
        b_filled = sum(1 for w in bundle_weeks for d in w["days"] if d["is_filled"])
        months_data.append({
            "month_index": m_idx,
            "name": name,
            "weeks_range": f"Minggu {w_start} - {w_end}",
            "total_count": b_total,
            "filled_count": b_filled,
            "missing_count": b_total - b_filled,
            "percentage": round((b_filled / b_total * 100), 1) if b_total > 0 else 0.0,
            "weeks": bundle_weeks
        })
        
    return {
        "total_days": total_days,
        "filled_days": filled_days,
        "missing_days": missing_days,
        "percentage": percentage,
        "months": months_data
    }

@app.post("/api/save-day")
def save_day(payload: SaveDayRequest):
    """Saves or updates an activity note for a specific date."""
    try:
        date_obj = datetime.datetime.strptime(payload.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
        
    save_note_to_month(date_obj, payload.note, "data")
    return {"status": "ok", "date": payload.date, "note": payload.note}

@app.post("/api/formalize")
def formalize_note(payload: FormalizeRequest):
    """Expands a brief activity bullet into a formal Indonesian sentence."""
    formalized = expand_narrative(payload.note)
    return {"status": "ok", "formalized": formalized}

@app.post("/api/batch-autofill")
def batch_autofill(payload: BatchAutofillRequest = Body(default=BatchAutofillRequest())):
    """Automatically fills missing dates with PT Naraya Telematika IT curriculum activities."""
    filled, empty = batch_autofill_notes(overwrite_existing=payload.overwrite_existing, data_dir="data")
    return {
        "status": "ok",
        "filled_count": filled,
        "message": f"Berhasil melengkapi {filled} tanggal kegiatan magang industri."
    }

@app.get("/api/config")
def get_config():
    """Reads current profile configuration from config.yaml."""
    return load_config("config.yaml")

@app.post("/api/config")
def update_config(payload: Dict[str, Any]):
    """Updates profile configuration in config.yaml."""
    try:
        with open("config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(payload, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return {"status": "ok", "message": "Konfigurasi profil berhasil diperbarui."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: PASS (`Ran 4 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add web/__init__.py web/app.py tests/test_web_api.py
git commit -m "feat: implement FastAPI app and calendar/data REST endpoints"
```

---

### Task 3: PDF Generation & Streaming Endpoints

**Files:**
- Modify: `web/app.py`
- Test: `tests/test_web_pdf.py`

**Interfaces:**
- Consumes:
  - `main.build_pdf_bundle`
  - `main.OUTPUT_MONTHLY_FILENAMES`
  - `main.CUMULATIVE_FILENAME`
  - `scripts.calendar_utils.get_month_bundle_weeks`
  - `scripts.calendar_utils.get_internship_calendar`
  - `scripts.data_manager.load_all_notes`
  - `main.load_config`
- Produces:
  - `POST /api/generate-pdf` (`target`: 1..6, "cumulative", "all")
  - `GET /api/pdf/{filename}` (Streams PDF with `Content-Disposition: inline`)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_web_pdf.py
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import os

class TestWebPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from web.app import app
        cls.client = TestClient(app)

    @patch("web.app.build_pdf_bundle")
    def test_generate_pdf_month_1(self, mock_build):
        mock_build.return_value = "output/Logbook_01_Juli_2026.pdf"
        res = self.client.post("/api/generate-pdf", json={"target": 1})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("Logbook_01_Juli_2026.pdf", data["pdf_url"])
        mock_build.assert_called_once()

    @patch("web.app.build_pdf_bundle")
    def test_generate_pdf_cumulative(self, mock_build):
        mock_build.return_value = "output/Logbook_Lengkap_Juli_Desember_2026.pdf"
        res = self.client.post("/api/generate-pdf", json={"target": "cumulative"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("Logbook_Lengkap_Juli_Desember_2026.pdf", data["pdf_url"])

    def test_stream_pdf_nonexistent(self):
        res = self.client.get("/api/pdf/nonexistent_file.pdf")
        self.assertEqual(res.status_code, 404)

    def test_stream_pdf_directory_traversal_attack(self):
        res = self.client.get("/api/pdf/../../etc/passwd")
        self.assertIn(res.status_code, [400, 404])

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_pdf.py`
Expected: FAIL with `AttributeError` or 404 for `/api/generate-pdf`

- [ ] **Step 3: Implement PDF endpoints in `web/app.py`**

Add imports and endpoints to `web/app.py`:
```python
# Add to imports in web/app.py:
from main import (
    build_pdf_bundle,
    OUTPUT_MONTHLY_FILENAMES,
    CUMULATIVE_FILENAME,
    ensure_assets
)

class GeneratePdfRequest(BaseModel):
    target: Any # 1..6 or "cumulative" or "all"

@app.post("/api/generate-pdf")
def generate_pdf(payload: GeneratePdfRequest):
    """Triggers XeLaTeX compilation for the requested target bundle."""
    ensure_assets()
    config = load_config("config.yaml")
    notes_map = load_all_notes("data")
    
    target = payload.target
    generated_urls = []
    
    if target == "all":
        # Compile all 6 monthly bundles + 1 cumulative
        for m_idx in range(1, 7):
            weeks = get_month_bundle_weeks(m_idx)
            out_name = OUTPUT_MONTHLY_FILENAMES[m_idx]
            build_pdf_bundle(weeks, notes_map, config, out_name)
            generated_urls.append(f"/api/pdf/{out_name}")
            
        all_weeks = get_internship_calendar()
        build_pdf_bundle(all_weeks, notes_map, config, CUMULATIVE_FILENAME)
        generated_urls.append(f"/api/pdf/{CUMULATIVE_FILENAME}")
        
        return {
            "status": "ok",
            "target": "all",
            "pdf_url": generated_urls[0],
            "all_urls": generated_urls,
            "message": "Semua 6 berkas PDF bulanan dan 1 berkas kumulatif berhasil dibuat."
        }
        
    elif target == "cumulative":
        all_weeks = get_internship_calendar()
        out_name = CUMULATIVE_FILENAME
        build_pdf_bundle(all_weeks, notes_map, config, out_name)
        return {
            "status": "ok",
            "target": "cumulative",
            "pdf_url": f"/api/pdf/{out_name}",
            "filename": out_name
        }
        
    else:
        try:
            m_idx = int(target)
            if m_idx not in OUTPUT_MONTHLY_FILENAMES:
                raise ValueError()
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Target bulan harus berupa angka 1 s/d 6, 'cumulative', atau 'all'.")
            
        weeks = get_month_bundle_weeks(m_idx)
        out_name = OUTPUT_MONTHLY_FILENAMES[m_idx]
        build_pdf_bundle(weeks, notes_map, config, out_name)
        return {
            "status": "ok",
            "target": m_idx,
            "pdf_url": f"/api/pdf/{out_name}",
            "filename": out_name
        }

@app.get("/api/pdf/{filename}")
def stream_pdf(filename: str):
    """Streams a generated PDF file from output/ directory inline for browser viewing."""
    # Prevent directory traversal
    clean_name = os.path.basename(filename)
    if clean_name != filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nama berkas tidak valid.")
        
    pdf_path = os.path.join("output", clean_name)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Berkas PDF belum digenerate. Silakan klik tombol 'Generate PDF' terlebih dahulu.")
        
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={clean_name}"}
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_pdf.py`
Expected: PASS (`Ran 4 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add web/app.py tests/test_web_pdf.py
git commit -m "feat: implement PDF generation and browser streaming endpoints"
```

---

### Task 4: Frontend HTML5 SPA Structure & Bento Dashboard

**Files:**
- Create: `web/static/index.html`
- Modify: `web/app.py` (mount static directory & index route)
- Test: `tests/test_web_static.py`

**Interfaces:**
- Consumes: `web/static/styles.css`, `web/static/app.js`
- Produces: Complete semantic HTML5 layout with Bento Grid container, Modals (Editor, PDF Preview, Config, Autofill Confirm), and Toast notifications.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_web_static.py
import unittest
from fastapi.testclient import TestClient
import os

class TestWebStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from web.app import app
        cls.client = TestClient(app)

    def test_serve_index_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("Log Book Magang Polinema", res.text)
        self.assertIn("bento-grid", res.text)
        self.assertIn("modal-editor", res.text)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: FAIL with 404 Not Found

- [ ] **Step 3: Implement `web/static/index.html` and static mount in `web/app.py`**

Mount static in `web/app.py`:
```python
# Add to web/app.py:
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html tidak ditemukan")
    return FileResponse(index_path, media_type="text/html")
```

Create `web/static/index.html`:
```html
<!DOCTYPE html>
<html lang="id" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Log Book Magang Polinema - PT Naraya Telematika</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <div id="app">
    <!-- Top Header & Navbar -->
    <header class="app-header">
      <div class="header-container">
        <div class="brand-group">
          <div class="logo-box">
            <span class="logo-icon">📘</span>
          </div>
          <div class="brand-info">
            <h1 class="brand-title">Log Book Magang Industri</h1>
            <p class="brand-subtitle">Politeknik Negeri Malang &bull; PT Naraya Telematika</p>
          </div>
        </div>

        <!-- Overall Progress Counter Card -->
        <div class="progress-pill">
          <div class="progress-stats">
            <span class="progress-label">Kelengkapan Log Book</span>
            <span class="progress-ratio" id="progress-ratio">0 / 158 Hari</span>
            <span class="progress-percent" id="progress-percent">0%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" id="progress-bar" style="width: 0%"></div>
          </div>
        </div>

        <!-- Action Header Buttons -->
        <div class="header-actions">
          <button id="btn-autofill" class="btn btn-emerald" title="Isi hari kosong secara otomatis">
            <span class="icon">⚡</span>
            <span>Lengkapi Kosong</span>
          </button>
          <button id="btn-open-pdf" class="btn btn-primary" title="Pratinjau & Buat Dokumen PDF">
            <span class="icon">📄</span>
            <span>Generate PDF</span>
          </button>
          <button id="btn-open-config" class="btn btn-outline" title="Pengaturan Identitas & Pembimbing">
            <span class="icon">⚙️</span>
          </button>
          <button id="btn-theme-toggle" class="btn btn-ghost" title="Ganti Mode Gelap/Terang">
            <span class="theme-icon">🌓</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="main-container">
      <!-- Month & Status Navigation Filters -->
      <section class="controls-card">
        <div class="month-tabs" id="month-tabs">
          <button class="tab-btn active" data-month="all">Semua Bulan</button>
          <button class="tab-btn" data-month="1">Juli 2026</button>
          <button class="tab-btn" data-month="2">Agustus 2026</button>
          <button class="tab-btn" data-month="3">September 2026</button>
          <button class="tab-btn" data-month="4">Oktober 2026</button>
          <button class="tab-btn" data-month="5">November 2026</button>
          <button class="tab-btn" data-month="6">Desember 2026</button>
        </div>

        <div class="filter-toggles">
          <span class="filter-label">Filter:</span>
          <button class="filter-btn active" data-filter="all">Semua</button>
          <button class="filter-btn" data-filter="missing">Belum Diisi</button>
          <button class="filter-btn" data-filter="filled">Sudah Diisi</button>
        </div>
      </section>

      <!-- Dynamic Bento Grid Container -->
      <section class="bento-grid" id="bento-container">
        <!-- Rendered reactively by app.js -->
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Memuat kalender dan catatan kegiatan...</p>
        </div>
      </section>
    </main>

    <!-- Modal: Daily Note Editor -->
    <div class="modal-overlay hidden" id="modal-editor">
      <div class="modal-dialog modal-md">
        <div class="modal-header">
          <div class="modal-title-group">
            <span class="badge badge-primary" id="editor-hari-badge">Senin</span>
            <h3 class="modal-title" id="editor-tanggal-title">1 Juli 2026</h3>
          </div>
          <button class="modal-close" data-close="modal-editor">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <div class="hours-info-box">
              <span class="hours-label">Jam Kerja:</span>
              <strong id="editor-hours">08.00 - 16.00 WIB</strong>
            </div>
          </div>
          <div class="form-group">
            <label for="editor-note" class="form-label">Catatan Kegiatan Harian:</label>
            <textarea id="editor-note" class="form-textarea" rows="4" placeholder="Ketik catatan kegiatan atau gunakan tombol bantuan di bawah..."></textarea>
          </div>
          <div class="editor-assist-bar">
            <button id="btn-formalize" class="btn btn-sm btn-outline-primary">
              <span>⚡ Formalize Narasi</span>
            </button>
            <button id="btn-suggest-task" class="btn btn-sm btn-outline">
              <span>💡 Saran Kegiatan IT</span>
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" data-close="modal-editor">Batal</button>
          <button id="btn-save-note" class="btn btn-primary">Simpan Catatan</button>
        </div>
      </div>
    </div>

    <!-- Modal: PDF Generator & Live Preview -->
    <div class="modal-overlay hidden" id="modal-pdf">
      <div class="modal-dialog modal-xl">
        <div class="modal-header">
          <div class="modal-title-group">
            <span class="icon">📄</span>
            <h3 class="modal-title">Pratinjau & Cetak Log Book PDF</h3>
          </div>
          <button class="modal-close" data-close="modal-pdf">&times;</button>
        </div>
        <div class="modal-body pdf-modal-body">
          <div class="pdf-controls-bar">
            <div class="form-inline">
              <label for="pdf-target-select">Pilih Berkas:</label>
              <select id="pdf-target-select" class="form-select">
                <option value="1">Bulan 1 (Juli 2026 - 5 Minggu)</option>
                <option value="2">Bulan 2 (Agustus 2026 - 4 Minggu)</option>
                <option value="3">Bulan 3 (September 2026 - 5 Minggu)</option>
                <option value="4">Bulan 4 (Oktober 2026 - 4 Minggu)</option>
                <option value="5">Bulan 5 (November 2026 - 4 Minggu)</option>
                <option value="6">Bulan 6 (Desember 2026 - 5 Minggu)</option>
                <option value="cumulative" selected>Lengkap Kumulatif (Juli - Desember, 27 Minggu)</option>
                <option value="all">Kompilasi Seluruh Bundel (6 Bulanan + 1 Kumulatif)</option>
              </select>
            </div>
            <button id="btn-trigger-compile" class="btn btn-primary">
              <span class="icon">⚙️</span>
              <span>Kompilasi PDF (XeLaTeX)</span>
            </button>
          </div>
          <div class="pdf-viewer-container" id="pdf-viewer-box">
            <div class="pdf-placeholder">
              <p>Pilih bundel dan klik <strong>Kompilasi PDF</strong> untuk melihat pratinjau live di sini.</p>
            </div>
            <iframe id="pdf-iframe" class="pdf-frame hidden" src="" title="PDF Preview"></iframe>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Config Profile -->
    <div class="modal-overlay hidden" id="modal-config">
      <div class="modal-dialog modal-lg">
        <div class="modal-header">
          <h3 class="modal-title">⚙️ Konfigurasi Profil & Pembimbing</h3>
          <button class="modal-close" data-close="modal-config">&times;</button>
        </div>
        <div class="modal-body">
          <form id="config-form">
            <h4 class="section-title">Data Mahasiswa</h4>
            <div class="form-row">
              <div class="form-col">
                <label class="form-label">Nama Mahasiswa</label>
                <input type="text" id="cfg-mhs-nama" class="form-input" required>
              </div>
              <div class="form-col">
                <label class="form-label">NIM</label>
                <input type="text" id="cfg-mhs-nim" class="form-input" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-col">
                <label class="form-label">Program Studi</label>
                <input type="text" id="cfg-mhs-prodi" class="form-input" required>
              </div>
              <div class="form-col">
                <label class="form-label">Mitra Magang</label>
                <input type="text" id="cfg-mhs-mitra" class="form-input" required>
              </div>
            </div>

            <h4 class="section-title">Dosen Pembimbing (Kampus)</h4>
            <div class="form-row">
              <div class="form-col">
                <label class="form-label">Nama Dosen Pembimbing</label>
                <input type="text" id="cfg-dosen-nama" class="form-input" required>
              </div>
              <div class="form-col">
                <label class="form-label">NIP</label>
                <input type="text" id="cfg-dosen-nip" class="form-input" required>
              </div>
            </div>

            <h4 class="section-title">Pembimbing Lapangan (Industri)</h4>
            <div class="form-row">
              <div class="form-col">
                <label class="form-label">Nama Pembimbing Lapangan</label>
                <input type="text" id="cfg-lapangan-nama" class="form-input" required>
              </div>
              <div class="form-col">
                <label class="form-label">NIK / ID Karyawan</label>
                <input type="text" id="cfg-lapangan-nik" class="form-input" required>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" data-close="modal-config">Tutup</button>
          <button id="btn-save-config" class="btn btn-primary">Simpan Perubahan</button>
        </div>
      </div>
    </div>

    <!-- Toast Notification Container -->
    <div id="toast-container" class="toast-container"></div>
  </div>
  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: PASS (`Ran 1 test in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add web/app.py web/static/index.html tests/test_web_static.py
git commit -m "feat: add HTML5 dashboard layout and static route mounting"
```

---

### Task 5: Modern Bento Grid CSS Design System & Dark Mode

**Files:**
- Create: `web/static/styles.css`
- Test: `tests/test_web_static.py` (verify styles.css served with CSS content-type)

**Interfaces:**
- Consumes: Google Fonts (`Inter`, `Fira Code`), CSS custom property tokens
- Produces: Complete responsive styling, light/dark themes, bento grid cards, badge components, modal styling, and micro-interactions.

- [ ] **Step 1: Write test assertion for CSS serving**

```python
# Add to tests/test_web_static.py:
    def test_serve_styles_css(self):
        res = self.client.get("/static/styles.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/css", res.headers.get("content-type", ""))
        self.assertIn("--primary:", res.text)
        self.assertIn("[data-theme=\"dark\"]", res.text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: FAIL (404 Not Found for `/static/styles.css`)

- [ ] **Step 3: Implement `web/static/styles.css`**

Create `web/static/styles.css`:
```css
/* web/static/styles.css */
/* Modern Bento Grid Design System for Polinema Log Book */

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Fira Code', monospace;

  /* Polinema Color Tokens */
  --primary: #2563EB;
  --primary-hover: #1D4ED8;
  --primary-light: #EFF6FF;
  --primary-border: #BFDBFE;

  --emerald: #059669;
  --emerald-hover: #047857;
  --emerald-light: #ECFDF5;
  --emerald-border: #A7F3D0;

  --amber: #D97706;
  --amber-light: #FEF3C7;
  --amber-border: #FDE68A;

  --rose: #E11D48;
  --rose-light: #FFE4E6;

  /* Theme: Light */
  --bg-app: #F8FAFC;
  --bg-surface: #FFFFFF;
  --bg-surface-elevated: #FFFFFF;
  --bg-subtle: #F1F5F9;
  
  --text-main: #0F172A;
  --text-muted: #64748B;
  --text-subtle: #94A3B8;

  --border-color: #E2E8F0;
  --border-focus: #3B82F6;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
  --shadow-modal: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-pill: 9999px;
  
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] {
  --bg-app: #090D16;
  --bg-surface: #131B2E;
  --bg-surface-elevated: #1E293B;
  --bg-subtle: #182238;

  --text-main: #F8FAFC;
  --text-muted: #94A3B8;
  --text-subtle: #64748B;

  --border-color: #26334D;
  --border-focus: #60A5FA;

  --primary-light: rgba(37, 99, 235, 0.15);
  --primary-border: rgba(96, 165, 250, 0.3);

  --emerald-light: rgba(5, 150, 105, 0.15);
  --emerald-border: rgba(52, 211, 153, 0.3);

  --amber-light: rgba(217, 119, 6, 0.15);
  --amber-border: rgba(251, 191, 36, 0.3);

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  --shadow-modal: 0 25px 35px -5px rgba(0, 0, 0, 0.7);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  background-color: var(--bg-app);
  color: var(--text-main);
  line-height: 1.5;
  transition: background-color var(--transition-normal), color var(--transition-normal);
}

/* Header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  padding: 0.75rem 1.5rem;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-box {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.brand-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Progress Pill */
.progress-pill {
  flex: 1;
  max-width: 360px;
  background-color: var(--bg-subtle);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-color);
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.progress-ratio {
  color: var(--primary);
}

.progress-percent {
  color: var(--emerald);
}

.progress-track {
  height: 6px;
  background: var(--border-color);
  border-radius: var(--radius-pill);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--emerald));
  border-radius: var(--radius-pill);
  transition: width var(--transition-normal);
}

/* Buttons */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 0.875rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-sm {
  font-size: 0.75rem;
  padding: 0.35rem 0.65rem;
}

.btn-primary {
  background-color: var(--primary);
  color: #FFFFFF;
}
.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-emerald {
  background-color: var(--emerald);
  color: #FFFFFF;
}
.btn-emerald:hover {
  background-color: var(--emerald-hover);
}

.btn-outline {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--text-main);
}
.btn-outline:hover {
  background-color: var(--bg-subtle);
}

.btn-outline-primary {
  background-color: transparent;
  border-color: var(--primary-border);
  color: var(--primary);
}
.btn-outline-primary:hover {
  background-color: var(--primary-light);
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
}
.btn-ghost:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}

/* Main Container */
.main-container {
  max-width: 1400px;
  margin: 1.5rem auto;
  padding: 0 1.5rem 3rem 1.5rem;
}

/* Controls Card */
.controls-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 0.75rem 1.25rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.month-tabs {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.tab-btn {
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-main);
  background: var(--bg-subtle);
}

.tab-btn.active {
  background: var(--primary);
  color: #FFFFFF;
}

.filter-toggles {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.75rem;
  color: var(--text-subtle);
  font-weight: 600;
}

.filter-btn {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-color);
  background: var(--bg-surface);
  color: var(--text-muted);
  cursor: pointer;
}

.filter-btn.active {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
}

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(620px, 1fr));
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
}

/* Week Bento Card */
.week-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.25rem;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  display: flex;
  flex-direction: column;
}

.week-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-border);
}

.week-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.week-title {
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  border-radius: var(--radius-pill);
}

.badge-primary {
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary-border);
}

.badge-emerald {
  background: var(--emerald-light);
  color: var(--emerald);
  border: 1px solid var(--emerald-border);
}

.badge-amber {
  background: var(--amber-light);
  color: var(--amber);
  border: 1px solid var(--amber-border);
}

/* Day List in Week Card */
.day-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.day-item {
  display: grid;
  grid-template-columns: 110px 100px 1fr 64px;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  background: var(--bg-subtle);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.day-item:hover {
  background: var(--bg-surface-elevated);
  border-color: var(--border-color);
}

.day-item.missing {
  border-left: 3px solid var(--amber);
}

.day-item.filled {
  border-left: 3px solid var(--emerald);
}

.day-meta {
  font-size: 0.8125rem;
  font-weight: 600;
}

.day-hours {
  font-size: 0.6875rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.day-note-preview {
  font-size: 0.8125rem;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.day-note-preview.empty {
  color: var(--amber);
  font-style: italic;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  transition: opacity var(--transition-fast);
}

.modal-overlay.hidden {
  display: none;
}

.modal-dialog {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalIn 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.96) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-md { max-width: 580px; }
.modal-lg { max-width: 720px; }
.modal-xl { max-width: 1080px; height: 85vh; }

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Form Styles */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 600;
  margin-bottom: 0.375rem;
  color: var(--text-main);
}

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-surface);
  color: var(--text-main);
  font-family: var(--font-sans);
  font-size: 0.875rem;
  transition: border-color var(--transition-fast);
}

.form-input:focus, .form-textarea:focus, .form-select:focus {
  outline: none;
  border-color: var(--border-focus);
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.form-col {
  flex: 1;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--primary);
  margin: 1rem 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hours-info-box {
  background: var(--bg-subtle);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  display: flex;
  justify-content: space-between;
}

.editor-assist-bar {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* PDF Viewer */
.pdf-modal-body {
  display: flex;
  flex-direction: column;
  padding: 0;
}

.pdf-controls-bar {
  padding: 0.75rem 1.25rem;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.pdf-viewer-container {
  flex: 1;
  background: #333333;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pdf-placeholder {
  color: #FFFFFF;
  font-size: 0.875rem;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

/* Spinner & Toast */
.loading-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-muted);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 800ms linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  background: var(--bg-surface);
  color: var(--text-main);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid var(--primary);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: toastIn 200ms ease;
}

.toast-success { border-left-color: var(--emerald); }
.toast-error { border-left-color: var(--rose); }

@keyframes toastIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add web/static/styles.css tests/test_web_static.py
git commit -m "feat: add Bento Grid CSS design system and dark mode tokens"
```

---

### Task 6: Frontend Reactive Client Logic & State Management

**Files:**
- Create: `web/static/app.js`
- Test: `tests/test_web_static.py` (verify app.js served and has valid syntax)

**Interfaces:**
- Consumes: REST API (`/api/calendar`, `/api/save-day`, `/api/formalize`, `/api/batch-autofill`, `/api/config`, `/api/generate-pdf`)
- Produces: Reactive state updates, modal controls, bento grid rendering, interactive note saving, live PDF preview in iframe.

- [ ] **Step 1: Write test assertion for `app.js`**

```python
# Add to tests/test_web_static.py:
    def test_serve_app_js(self):
        res = self.client.get("/static/app.js")
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.headers.get("content-type", ""))
        self.assertIn("fetchCalendar", res.text)
        self.assertIn("formalizeNote", res.text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: FAIL (404 Not Found for `/static/app.js`)

- [ ] **Step 3: Implement `web/static/app.js`**

Create `web/static/app.js`:
```javascript
// web/static/app.js
/**
 * Polinema Log Book Client Application.
 * Reactive Vanilla JS SPA State Manager & API Orchestrator.
 */

(function () {
  'use strict';

  // State
  const state = {
    calendar: null,
    activeMonth: 'all',     // 'all' or 1..6
    activeFilter: 'all',    // 'all', 'missing', 'filled'
    activeEditingDay: null, // { date, hari, tanggal_str, jam_masuk, jam_pulang, note }
    theme: localStorage.getItem('logbook_theme') || 'light',
  };

  // DOM Elements
  const dom = {
    bentoContainer: document.getElementById('bento-container'),
    progressRatio: document.getElementById('progress-ratio'),
    progressPercent: document.getElementById('progress-percent'),
    progressBar: document.getElementById('progress-bar'),
    monthTabs: document.getElementById('month-tabs'),
    filterButtons: document.querySelectorAll('.filter-btn'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    btnAutofill: document.getElementById('btn-autofill'),
    btnOpenPdf: document.getElementById('btn-open-pdf'),
    btnOpenConfig: document.getElementById('btn-open-config'),
    toastContainer: document.getElementById('toast-container'),

    // Modals
    modalEditor: document.getElementById('modal-editor'),
    editorHariBadge: document.getElementById('editor-hari-badge'),
    editorTanggalTitle: document.getElementById('editor-tanggal-title'),
    editorHours: document.getElementById('editor-hours'),
    editorNote: document.getElementById('editor-note'),
    btnFormalize: document.getElementById('btn-formalize'),
    btnSuggestTask: document.getElementById('btn-suggest-task'),
    btnSaveNote: document.getElementById('btn-save-note'),

    modalPdf: document.getElementById('modal-pdf'),
    pdfTargetSelect: document.getElementById('pdf-target-select'),
    btnTriggerCompile: document.getElementById('btn-trigger-compile'),
    pdfIframe: document.getElementById('pdf-iframe'),
    pdfPlaceholder: document.querySelector('.pdf-placeholder'),

    modalConfig: document.getElementById('modal-config'),
    btnSaveConfig: document.getElementById('btn-save-config'),
    cfgMhsNama: document.getElementById('cfg-mhs-nama'),
    cfgMhsNim: document.getElementById('cfg-mhs-nim'),
    cfgMhsProdi: document.getElementById('cfg-mhs-prodi'),
    cfgMhsMitra: document.getElementById('cfg-mhs-mitra'),
    cfgDosenNama: document.getElementById('cfg-dosen-nama'),
    cfgDosenNip: document.getElementById('cfg-dosen-nip'),
    cfgLapanganNama: document.getElementById('cfg-lapangan-nama'),
    cfgLapanganNik: document.getElementById('cfg-lapangan-nik'),
  };

  // Utilities
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    dom.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('logbook_theme', theme);
    state.theme = theme;
  }

  // API Calls
  async function fetchCalendar() {
    try {
      const res = await fetch('/api/calendar');
      if (!res.ok) throw new Error('Gagal memuat kalender');
      state.calendar = await res.json();
      renderApp();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveDayNote(dateStr, noteText) {
    try {
      const res = await fetch('/api/save-day', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: dateStr, note: noteText }),
      });
      if (!res.ok) throw new Error('Gagal menyimpan catatan');
      showToast(`Catatan untuk ${dateStr} berhasil disimpan`, 'success');
      closeModal(dom.modalEditor);
      await fetchCalendar();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function formalizeCurrentNote() {
    const rawNote = dom.editorNote.value.trim();
    if (!rawNote) {
      showToast('Ketik catatan terlebih dahulu sebelum diformalkan.', 'error');
      return;
    }
    try {
      dom.btnFormalize.disabled = true;
      dom.btnFormalize.innerText = '⚡ Memproses...';
      const res = await fetch('/api/formalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: rawNote }),
      });
      if (!res.ok) throw new Error('Gagal memformalkan narasi');
      const data = await res.json();
      dom.editorNote.value = data.formalized;
      showToast('Narasi berhasil diformalkan!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnFormalize.disabled = false;
      dom.btnFormalize.innerText = '⚡ Formalize Narasi';
    }
  }

  async function triggerBatchAutofill() {
    const confirmRun = confirm(
      'Apakah Anda yakin ingin mengisi semua hari kerja aktif yang masih kosong dengan kurikulum kegiatan IT PT Naraya Telematika?\n\nCatatan yang sudah diisi manual tidak akan ditimpa.'
    );
    if (!confirmRun) return;

    try {
      dom.btnAutofill.disabled = true;
      dom.btnAutofill.innerHTML = '<span class="icon">⏳</span><span>Mengisi...</span>';
      const res = await fetch('/api/batch-autofill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overwrite_existing: false }),
      });
      if (!res.ok) throw new Error('Gagal mengisi otomatis');
      const data = await res.json();
      showToast(data.message, 'success');
      await fetchCalendar();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnAutofill.disabled = false;
      dom.btnAutofill.innerHTML = '<span class="icon">⚡</span><span>Lengkapi Kosong</span>';
    }
  }

  async function loadConfigData() {
    try {
      const res = await fetch('/api/config');
      if (!res.ok) throw new Error('Gagal memuat konfigurasi');
      const cfg = await res.json();
      const mhs = cfg.mahasiswa || {};
      const dosen = (cfg.pembimbing && cfg.pembimbing.dosen) || {};
      const lapangan = (cfg.pembimbing && cfg.pembimbing.lapangan) || {};

      dom.cfgMhsNama.value = mhs.nama || '';
      dom.cfgMhsNim.value = mhs.nim || '';
      dom.cfgMhsProdi.value = mhs.prodi || '';
      dom.cfgMhsMitra.value = mhs.mitra || '';
      dom.cfgDosenNama.value = dosen.nama || '';
      dom.cfgDosenNip.value = dosen.nip || '';
      dom.cfgLapanganNama.value = lapangan.nama || '';
      dom.cfgLapanganNik.value = lapangan.nik || '';

      openModal(dom.modalConfig);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveConfigData() {
    const payload = {
      mahasiswa: {
        nama: dom.cfgMhsNama.value.trim(),
        nim: dom.cfgMhsNim.value.trim(),
        prodi: dom.cfgMhsProdi.value.trim(),
        mitra: dom.cfgMhsMitra.value.trim(),
      },
      pembimbing: {
        dosen: {
          nama: dom.cfgDosenNama.value.trim(),
          nip: dom.cfgDosenNip.value.trim(),
        },
        lapangan: {
          nama: dom.cfgLapanganNama.value.trim(),
          nik: dom.cfgLapanganNik.value.trim(),
        },
      },
      pengaturan: {
        jam_kerja: {
          senin_jumat: { masuk: '08.00', pulang: '16.00' },
          sabtu: { masuk: '08.00', pulang: '14.00' },
        },
      },
    };

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Gagal memperbarui konfigurasi');
      showToast('Konfigurasi profil berhasil diperbarui', 'success');
      closeModal(dom.modalConfig);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function compileAndPreviewPdf() {
    const target = dom.pdfTargetSelect.value;
    try {
      dom.btnTriggerCompile.disabled = true;
      dom.btnTriggerCompile.innerHTML = '<span class="icon">⏳</span><span>Kompilasi...</span>';

      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target }),
      });
      if (!res.ok) throw new Error('Kompilasi XeLaTeX gagal');
      const data = await res.json();

      dom.pdfPlaceholder.classList.add('hidden');
      dom.pdfIframe.classList.remove('hidden');
      dom.pdfIframe.src = `${data.pdf_url}?t=${Date.now()}`;
      showToast('Berkas PDF berhasil dikompilasi!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnTriggerCompile.disabled = false;
      dom.btnTriggerCompile.innerHTML = '<span class="icon">⚙️</span><span>Kompilasi PDF (XeLaTeX)</span>';
    }
  }

  // Modals Control
  function openModal(modal) {
    modal.classList.remove('hidden');
  }

  function closeModal(modal) {
    modal.classList.add('hidden');
  }

  function openEditor(day) {
    state.activeEditingDay = day;
    dom.editorHariBadge.innerText = day.hari;
    dom.editorTanggalTitle.innerText = day.tanggal_str;
    dom.editorHours.innerText = `${day.jam_masuk} - ${day.jam_pulang} WIB`;
    dom.editorNote.value = day.note || '';
    openModal(dom.modalEditor);
  }

  // Rendering
  function renderApp() {
    if (!state.calendar) return;

    // 1. Progress Bar
    const total = state.calendar.total_days;
    const filled = state.calendar.filled_days;
    const percent = state.calendar.percentage;
    dom.progressRatio.innerText = `${filled} / ${total} Hari`;
    dom.progressPercent.innerText = `${percent}%`;
    dom.progressBar.style.width = `${percent}%`;

    // 2. Bento Grid
    dom.bentoContainer.innerHTML = '';

    // Filter months
    let targetMonths = state.calendar.months;
    if (state.activeMonth !== 'all') {
      const mIdx = parseInt(state.activeMonth, 10);
      targetMonths = targetMonths.filter((m) => m.month_index === mIdx);
    }

    targetMonths.forEach((month) => {
      month.weeks.forEach((week) => {
        // Filter days based on status filter
        let filteredDays = week.days;
        if (state.activeFilter === 'missing') {
          filteredDays = filteredDays.filter((d) => !d.is_filled);
        } else if (state.activeFilter === 'filled') {
          filteredDays = filteredDays.filter((d) => d.is_filled);
        }

        // If filter results in empty week, skip or show empty note
        if (filteredDays.length === 0 && state.activeFilter !== 'all') {
          return;
        }

        const card = document.createElement('div');
        card.className = 'week-card';

        const weekHeader = document.createElement('div');
        weekHeader.className = 'week-header';
        weekHeader.innerHTML = `
          <div class="week-title">
            <span>Minggu ke-${week.minggu_ke}</span>
            <span class="badge badge-primary">${month.name}</span>
          </div>
          <span class="badge ${week.days.every((d) => d.is_filled) ? 'badge-emerald' : 'badge-amber'}">
            ${week.days.filter((d) => d.is_filled).length} / ${week.days.length} Terisi
          </span>
        `;
        card.appendChild(weekHeader);

        const dayList = document.createElement('div');
        dayList.className = 'day-list';

        filteredDays.forEach((d) => {
          const item = document.createElement('div');
          item.className = `day-item ${d.is_filled ? 'filled' : 'missing'}`;

          const hasNote = d.is_filled && d.note;
          const noteText = hasNote ? d.note : 'Belum ada catatan kegiatan';

          item.innerHTML = `
            <div class="day-meta">${d.hari}, ${d.tanggal_str.split(' ')[0]} ${d.tanggal_str.split(' ')[1].slice(0, 3)}</div>
            <div class="day-hours">${d.jam_masuk}-${d.jam_pulang}</div>
            <div class="day-note-preview ${hasNote ? '' : 'empty'}" title="${noteText}">${noteText}</div>
            <button class="btn btn-sm btn-outline-primary btn-edit-day">Edit</button>
          `;

          item.querySelector('.btn-edit-day').addEventListener('click', () => openEditor(d));
          dayList.appendChild(item);
        });

        card.appendChild(dayList);
        dom.bentoContainer.appendChild(card);
      });
    });

    if (dom.bentoContainer.children.length === 0) {
      dom.bentoContainer.innerHTML = `
        <div class="loading-state">
          <p>Tidak ada kegiatan yang sesuai dengan filter yang dipilih.</p>
        </div>
      `;
    }
  }

  // Event Listeners Initialization
  function initEvents() {
    // Theme toggle
    dom.btnThemeToggle.addEventListener('click', () => {
      applyTheme(state.theme === 'light' ? 'dark' : 'light');
    });

    // Month tabs
    dom.monthTabs.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        dom.monthTabs.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeMonth = btn.getAttribute('data-month');
        renderApp();
      });
    });

    // Status filter buttons
    dom.filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        dom.filterButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeFilter = btn.getAttribute('data-filter');
        renderApp();
      });
    });

    // Modal Close buttons
    document.querySelectorAll('[data-close]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const modalId = btn.getAttribute('data-close');
        const modal = document.getElementById(modalId);
        if (modal) closeModal(modal);
      });
    });

    // Editor Actions
    dom.btnFormalize.addEventListener('click', formalizeCurrentNote);
    dom.btnSuggestTask.addEventListener('click', () => {
      if (!dom.editorNote.value) {
        dom.editorNote.value = 'Mempelajari modul sistem dan koordinasi dengan tim pengembang';
      }
      formalizeCurrentNote();
    });
    dom.btnSaveNote.addEventListener('click', () => {
      if (state.activeEditingDay) {
        saveDayNote(state.activeEditingDay.date, dom.editorNote.value.trim());
      }
    });

    // Header Action Modals
    dom.btnAutofill.addEventListener('click', triggerBatchAutofill);
    dom.btnOpenConfig.addEventListener('click', loadConfigData);
    dom.btnSaveConfig.addEventListener('click', (e) => {
      e.preventDefault();
      saveConfigData();
    });

    dom.btnOpenPdf.addEventListener('click', () => {
      openModal(dom.modalPdf);
    });
    dom.btnTriggerCompile.addEventListener('click', compileAndPreviewPdf);
  }

  // Boot
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(state.theme);
    initEvents();
    fetchCalendar();
  });
})();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: PASS (`Ran 3 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add web/static/app.js tests/test_web_static.py
git commit -m "feat: implement frontend reactive SPA client and state manager"
```

---

### Task 7: CLI Integration (`main.py --ui`) & Full E2E Verification

**Files:**
- Modify: `main.py`
- Test: `tests/test_cli_ui.py`

**Interfaces:**
- Consumes: `web.app.app`, `uvicorn`
- Produces: CLI `--ui` flag with optional `--port` and `--host` arguments.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli_ui.py
import unittest
import subprocess
import sys

class TestCliUiFlag(unittest.TestCase):
    def test_cli_help_includes_ui_flag(self):
        res = subprocess.run([sys.executable, "main.py", "--help"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--ui", res.stdout)
        self.assertIn("dashboard", res.stdout.lower())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_cli_ui.py`
Expected: FAIL with `AssertionError: '--ui' not found in ...`

- [ ] **Step 3: Update `main.py` to support `--ui` flag**

In `main.py`:
```python
# In main.py, add arguments to parser:
    parser.add_argument("--ui", action="store_true", help="Jalankan antarmuka web dashboard interaktif")
    parser.add_argument("--port", type=int, default=8000, help="Port server web UI (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host server web UI (default: 127.0.0.1)")

# In main() execution logic:
    if args.ui:
        import uvicorn
        ensure_assets()
        init_data_files("data")
        print(f"\n========================================================")
        print(f"🚀 Log Book Polinema Web Dashboard Berjalan!")
        print(f"📍 Akses di peramban web: http://{args.host}:{args.port}")
        print(f"========================================================\n")
        uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
        sys.exit(0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_cli_ui.py`
Expected: PASS (`Ran 1 test in ... OK`)

Run full test suite:
Run: `python3 -m unittest discover tests`
Expected: ALL tests pass (40+ tests across existing and new modules).

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_cli_ui.py
git commit -m "feat: add CLI --ui flag to launch local web dashboard via uvicorn"
```

---

## Self-Review Checklist

1. **Spec Coverage:**
   - Visual progress tracking (158 days July–Dec 2026): Covered in `web/app.py:get_calendar` and `web/static/app.js`.
   - Edit notes without touching YAML: Covered in `POST /api/save-day` and Modal Editor.
   - 1-click note formalization: Covered in `POST /api/formalize` and `⚡ Formalize Narasi`.
   - Batch auto-fill with IT curriculum: Covered in `scripts/curriculum.py` and `POST /api/batch-autofill`.
   - Profile update in `config.yaml`: Covered in `GET/POST /api/config` and Modal Config.
   - Live PDF preview in browser: Covered in `POST /api/generate-pdf`, `GET /api/pdf/{filename}`, and `<iframe>` viewer.
   - CLI flag `python3 main.py --ui`: Covered in `main.py` and `test_cli_ui.py`.

2. **Placeholder Scan:**
   - No `TODO`, `TBD`, or "implement later".
   - Full code blocks for all files, schemas, endpoints, tests, HTML, CSS, and JS.

3. **Type and Interface Consistency:**
   - `get_curriculum_task`, `batch_autofill_notes`, `get_calendar`, `save_day`, `formalize_note`, `generate_pdf`, and `stream_pdf` signatures are completely consistent across tasks.
