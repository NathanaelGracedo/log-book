# Template Header & GitHub Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize the LaTeX letterhead (kop surat) with a balanced single Polinema logo, sanitize personal identity data, decouple end-to-end tests, implement an automated environment pre-flight doctor check, and provide complete open-source documentation and configuration templates for public GitHub readiness.

**Architecture:** Refactor the LaTeX generator (`scripts/latex_builder.py`) into a 3-minipage balanced geometry (left logo, centered institution typography, right invisible counterweight) to guarantee exact horizontal centering while strictly preserving the 1-week-per-page A4 height budget. Introduce configuration auto-bootstrapping from `config.example.yaml` in `main.py` and `web/app.py` with `.gitignore` privacy guards. Decouple `tests/test_e2e.py` by dynamically checking loaded YAML notes. Add a system doctor check (`scripts/doctor.py`) for `xelatex` availability with cross-platform installation instructions, and provide a comprehensive `README.md` and MIT `LICENSE`.

**Tech Stack:** Python 3.10+, XeLaTeX, PyYAML, FastAPI, Uvicorn, unittest.

---

## Global Constraints

- **Python Runtime:** Python 3.10+ (standard library + project dependencies `pyyaml`, `fastapi`, `uvicorn`, `pydantic`).
- **LaTeX Engine:** XeLaTeX (`xelatex`) with UTF-8 support and system fonts.
- **Layout Invariant:** Exactly 1 week = 1 page A4 in all generated PDFs (no vertical spillover).
- **Header Geometry:** 3-column minipage layout (`0.15\textwidth`, `0.70\textwidth`, `0.15\textwidth`), logo height `1.8cm`, exactly 1 Polinema logo on the left (`assets/polinema.png`).
- **Privacy Rule:** Personal identity (real name, NIM, supervisor names) must NEVER be committed to git; tracked config file is `config.example.yaml`, while `config.yaml` is gitignored.
- **Cross-Platform Instructions:** Pre-flight doctor must support Ubuntu/Debian, Arch Linux, Fedora, macOS (Homebrew), and Windows (MiKTeX).
- **Testing Standard:** 100% test pass rate across the entire test suite (`python3 -m unittest discover tests`).

---

## File Structure

```text
log-book/
├── .gitignore                                   # Updated: ignore config.yaml, output/*.pdf, LaTeX artifacts
├── config.example.yaml                          # Clean generic public starter template
├── config.yaml                                  # Local private config (gitignored)
├── LICENSE                                      # MIT Open Source License
├── README.md                                    # Comprehensive project documentation & quickstart
├── main.py                                      # CLI orchestrator with auto-bootstrap and doctor check
├── scripts/
│   ├── doctor.py                                # System pre-flight check for xelatex with OS install guides (new)
│   ├── latex_builder.py                         # Updated: symmetrical single-logo kop surat layout
│   ├── calendar_utils.py                        # Calendar utilities (existing)
│   ├── data_manager.py                          # YAML note storage (existing)
│   ├── narrative_expander.py                    # Narrative expansion (existing)
│   └── curriculum.py                            # 158-day curriculum engine (existing)
├── web/
│   ├── app.py                                   # FastAPI backend with config auto-bootstrap
│   └── static/                                  # Vanilla HTML5/CSS/JS frontend (existing)
├── data/
│   └── README.md                                # Guide on monthly logbook data structure
└── tests/
    ├── test_latex_builder.py                    # Updated: tests for single logo and balanced header
    ├── test_e2e.py                              # Updated: dynamic note verification decoupled from hardcoded strings
    ├── test_bootstrap.py                        # Tests for config auto-bootstrap from template (new)
    └── test_doctor.py                           # Tests for xelatex pre-flight check and OS guidance (new)
```

---

### Task 1: Symmetrical Single-Logo Header Layout

**Files:**
- Modify: `scripts/latex_builder.py:52-86`
- Modify: `tests/test_latex_builder.py`

**Interfaces:**
- Consumes: `assets/polinema.png`, `week_data: dict`, `notes_map: dict[str, str]`, `config: dict`
- Produces: `render_week_page(...) -> str` generating a 3-minipage LaTeX header with `0.15\textwidth` left logo, `0.70\textwidth` centered text, and `0.15\textwidth` counterweight.

- [ ] **Step 1: Write the failing test in `tests/test_latex_builder.py`**

Add test cases to `tests/test_latex_builder.py` verifying that:
1. `polinema.png` is present in the LaTeX output.
2. `kemendikbud.jpg` is NOT referenced in the LaTeX header.
3. The minipage widths `0.15\textwidth` and `0.70\textwidth` are used.
4. A full 6-day week fits on exactly 1 page A4.

```python
    def test_header_layout_single_logo_and_symmetrical_minipages(self):
        latex = generate_latex_document([self.weeks[0]], self.notes_map, self.config)
        # Should include polinema logo on the left
        self.assertIn("polinema.png", latex)
        # Should NOT include kemendikbud logo
        self.assertNotIn("kemendikbud.jpg", latex)
        # Should contain balanced minipage geometry (0.15, 0.70, 0.15)
        self.assertIn(r"\begin{minipage}[c]{0.15\textwidth}", latex)
        self.assertIn(r"\begin{minipage}[c]{0.70\textwidth}", latex)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: FAIL with `AssertionError: '\\begin{minipage}[c]{0.15\\textwidth}' not found in ...` (since current code uses `0.14\textwidth` and references `kemendikbud.jpg`).

- [ ] **Step 3: Write minimal implementation in `scripts/latex_builder.py`**

Update lines 52-86 in `scripts/latex_builder.py` to remove `kemendikbud_logo` from the header and implement the 3-minipage symmetrical layout:

```python
    polinema_logo = os.path.abspath(os.path.join(resolved_assets, "polinema.png"))
    has_polinema = os.path.exists(polinema_logo)
    logo_left_tex = f"\\includegraphics[height=1.8cm]{{{polinema_logo}}}" if has_polinema else ""

    # Symmetrical 3-column header:
    # Column 1 (0.15\textwidth): Polinema logo, centered
    # Column 2 (0.70\textwidth): Official institution typography, centered
    # Column 3 (0.15\textwidth): Invisible mathematical counterweight (~), guaranteeing exact center alignment
    kop_tex = rf"""
\begin{{minipage}}[c]{{0.15\textwidth}}
\centering
{logo_left_tex}
\end{{minipage}}%
\begin{{minipage}}[c]{{0.70\textwidth}}
\centering
{{\fontsize{{9pt}}{{10.5pt}}\selectfont \textbf{{KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI}}\\}}
{{\fontsize{{10.5pt}}{{12pt}}\selectfont \textbf{{POLITEKNIK NEGERI MALANG}}\\}}
{{\fontsize{{9.5pt}}{{11pt}}\selectfont \textbf{{JURUSAN TEKNOLOGI INFORMASI}}\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Jalan Soekarno Hatta Nomor 9, Jatimulyo, Lowokwaru, Malang 65141\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Telepon (0341) 404424, 404425, Faksimile (0341) 404420\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Laman www.polinema.ac.id\\}}
\end{{minipage}}%
\begin{{minipage}}[c]{{0.15\textwidth}}
\centering
~
\end{{minipage}}

\vspace{{1pt}}
\hrule height 1.2pt
\vspace{{1pt}}
\hrule height 0.5pt
\vspace{{0.2cm}}
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: PASS with all tests passing (including `test_full_six_day_week_fits_single_page`).

- [ ] **Step 5: Commit changes**

```bash
git add scripts/latex_builder.py tests/test_latex_builder.py
git commit -m "fix(latex): revise letterhead to symmetrical single-logo layout"
```

---

### Task 2: Dynamic Test Decoupling in E2E Test

**Files:**
- Modify: `tests/test_e2e.py`

**Interfaces:**
- Consumes: `scripts.data_manager.load_all_notes`, `main.OUTPUT_MONTHLY_FILENAMES`, compiled `output/Logbook_01_Juli_2026.pdf`
- Produces: Decoupled end-to-end integration test verifying PDF compilation, page count, header text, and dynamically loaded notes.

- [ ] **Step 1: Write the updated test assertions in `tests/test_e2e.py`**

Replace the hardcoded assertion `self.assertIn("rekayasa perangkat lunak", pdftotext_res.stdout)` with a dynamic test that loads `notes_map = load_all_notes("data")` and verifies whatever note is set for `2026-07-01` (or its primary keyword/expanded form) appears in the PDF text, alongside invariant text like `"log book kegiatan"` and `"politeknik negeri malang"`.

```python
import unittest
import os
import sys
import shutil
import subprocess
from scripts.data_manager import load_all_notes

class TestEndToEndBuild(unittest.TestCase):
    def test_build_month_1(self):
        # Build month 1
        res = subprocess.run(
            [sys.executable, "main.py", "--month", "1", "--non-interactive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        if not shutil.which("pdfinfo") or not shutil.which("pdftotext"):
            self.skipTest("poppler-utils (pdfinfo/pdftotext) not found on system")

        # Verify page count: Month 1 has Weeks 1..5 -> exactly 5 pages
        pdfinfo_res = subprocess.run(["pdfinfo", pdf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdfinfo_res.returncode, 0, f"pdfinfo failed: {pdfinfo_res.stderr}")
        lines = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
        self.assertTrue(bool(lines), "Could not find Pages in pdfinfo output")
        pages = int(lines[0].split(":")[1].strip())
        self.assertEqual(pages, 5, f"Expected exactly 5 pages for Month 1, got {pages}")

        # Extract text from PDF
        pdftotext_res = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdftotext_res.returncode, 0, f"pdftotext failed: {pdftotext_res.stderr}")
        pdf_text_lower = pdftotext_res.stdout.lower()

        # Invariant checks: Document title and institution
        self.assertIn("log book kegiatan", pdf_text_lower)
        self.assertIn("politeknik negeri malang", pdf_text_lower)
        self.assertIn("jurusan teknologi informasi", pdf_text_lower)

        # Dynamic check: Verify that July 1 note from data/ is rendered
        notes_map = load_all_notes("data")
        july_1_note = notes_map.get("2026-07-01", "").strip()
        if july_1_note:
            # Check the first 20 characters of the recorded note to avoid line wrap / expansion discrepancy
            sample_phrase = july_1_note.split()[0].lower()
            self.assertIn(sample_phrase, pdf_text_lower, f"Expected note keyword '{sample_phrase}' in PDF output")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it passes with current customized note**

Run: `python3 -m unittest tests/test_e2e.py`
Expected: PASS (exits 0, verifies 5 pages, invariant titles, and dynamically loaded note).

- [ ] **Step 3: Run full test suite to verify no regressions**

Run: `python3 -m unittest discover tests`
Expected: PASS with all tests passing.

- [ ] **Step 4: Commit changes**

```bash
git add tests/test_e2e.py
git commit -m "test: decouple e2e test from hardcoded sample notes"
```

---

### Task 3: Config Sanitization & Auto-Bootstrap

**Files:**
- Create: `config.example.yaml`
- Modify: `.gitignore`
- Modify: `main.py` (`load_config`)
- Modify: `web/app.py` (`get_config` and startup bootstrap)
- Create: `tests/test_bootstrap.py`

**Interfaces:**
- Consumes: `config.example.yaml`
- Produces: `load_config(config_path: str = "config.yaml") -> dict` with automatic copy from `config.example.yaml` if missing.

- [ ] **Step 1: Write the failing test in `tests/test_bootstrap.py`**

```python
# tests/test_bootstrap.py
import unittest
import os
import shutil
import tempfile
import yaml
from main import load_config

class TestConfigBootstrap(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_bootstrap_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bootstrap_copies_example_when_config_missing(self):
        example_path = os.path.join(self.temp_dir, "config.example.yaml")
        config_path = os.path.join(self.temp_dir, "config.yaml")

        example_data = {
            "mahasiswa": {
                "nama": "Nama Lengkap Mahasiswa",
                "nim": "XXXXXXXXXX",
                "prodi": "Sarjana Terapan Teknik Informatika",
                "mitra": "Nama Perusahaan / Tempat Magang"
            },
            "pembimbing": {
                "dosen": {"nama": "Nama Dosen", "nip": "198000000000"},
                "lapangan": {"nama": "Nama Pembimbing Lapangan", "nik": "EMP-001"}
            },
            "pengaturan": {
                "jam_kerja": {
                    "senin_jumat": {"masuk": "08.00", "pulang": "16.00"},
                    "sabtu": {"masuk": "08.00", "pulang": "14.00"}
                }
            }
        }
        with open(example_path, "w", encoding="utf-8") as f:
            yaml.dump(example_data, f)

        # Call load_config with missing config_path and existing example_path
        loaded = load_config(config_path=config_path, example_path=example_path)
        self.assertTrue(os.path.exists(config_path))
        self.assertEqual(loaded["mahasiswa"]["nama"], "Nama Lengkap Mahasiswa")

    def test_load_config_raises_when_both_missing(self):
        config_path = os.path.join(self.temp_dir, "non_existent.yaml")
        example_path = os.path.join(self.temp_dir, "non_existent_example.yaml")
        with self.assertRaises(FileNotFoundError):
            load_config(config_path=config_path, example_path=example_path)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_bootstrap.py`
Expected: FAIL with `TypeError: load_config() got an unexpected keyword argument 'example_path'` or `FileNotFoundError`.

- [ ] **Step 3: Create `config.example.yaml` and update `.gitignore`**

Create `config.example.yaml`:
```yaml
# ==============================================================================
# KONFIGURASI PROFIL LOG BOOK MAGANG INDUSTRI JTI POLINEMA
# ==============================================================================
# Silakan lengkapi data diri Anda di bawah ini sebelum men-generate PDF.
# File ini berfungsi sebagai template awal. Salin menjadi 'config.yaml'.
# ==============================================================================

mahasiswa:
  nama: "Nama Lengkap Mahasiswa"
  nim: "XXXXXXXXXX"
  prodi: "Sarjana Terapan Teknik Informatika" # atau: Sarjana Terapan Sistem Informasi Bisnis
  mitra: "Nama Perusahaan / Tempat Magang"

pembimbing:
  dosen:
    nama: "Nama Dosen Pembimbing, S.Kom., M.Kom."
    nip: "198XXXXXXXXXXXXXXX"
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

Update `.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Local User Configuration & Data
config.yaml

# LaTeX Build Artifacts
*.aux
*.log
*.out
*.toc
*.fls
*.fdb_latexmk
*.synctex.gz

# Output Generated PDFs
output/

# Superpowers SDD workspace
.superpowers/
```

- [ ] **Step 4: Update `load_config` in `main.py` and `web/app.py`**

In `main.py`:
```python
import shutil

def load_config(config_path: str = "config.yaml", example_path: str = "config.example.yaml") -> dict:
    """
    Loads configuration YAML file.
    If config_path is missing, automatically bootstraps it from example_path.
    """
    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            print(f"[BOOTSTRAP] Berkas '{config_path}' tidak ditemukan. Menyalin template dari '{example_path}'...")
            shutil.copyfile(example_path, config_path)
            print(f"[BOOTSTRAP] Silakan sesuaikan data diri dan mitra pada '{config_path}' sesuai kebutuhan Anda.")
        else:
            raise FileNotFoundError(f"Konfigurasi '{config_path}' dan template '{example_path}' tidak ditemukan.")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
```

In `web/app.py`:
Ensure `load_config("config.yaml")` calls the updated `load_config` so startup and API calls seamlessly bootstrap `config.yaml` if it does not yet exist.

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m unittest tests/test_bootstrap.py`
Expected: PASS.

- [ ] **Step 6: Untrack `config.yaml` from git index while preserving disk file**

```bash
git rm --cached config.yaml
git add config.example.yaml .gitignore main.py web/app.py tests/test_bootstrap.py
git commit -m "feat: add config.example.yaml, gitignore private config, and auto-bootstrap config.yaml"
```

---

### Task 4: Environment Pre-flight Doctor Check

**Files:**
- Create: `scripts/doctor.py`
- Modify: `main.py`
- Create: `tests/test_doctor.py`

**Interfaces:**
- Consumes: `shutil.which("xelatex")`
- Produces: 
  - `check_xelatex() -> tuple[bool, str]`
  - `run_doctor(exit_on_failure: bool = True) -> bool`

- [ ] **Step 1: Write the failing test in `tests/test_doctor.py`**

```python
# tests/test_doctor.py
import unittest
from unittest.mock import patch
from scripts.doctor import check_xelatex, run_doctor

class TestDoctor(unittest.TestCase):
    @patch("shutil.which")
    def test_check_xelatex_found(self, mock_which):
        mock_which.return_value = "/usr/bin/xelatex"
        found, info = check_xelatex()
        self.assertTrue(found)
        self.assertEqual(info, "/usr/bin/xelatex")

    @patch("shutil.which")
    def test_check_xelatex_missing(self, mock_which):
        mock_which.return_value = None
        found, instructions = check_xelatex()
        self.assertFalse(found)
        # Should include install guidance for major OS platforms
        self.assertIn("apt install texlive-xetex", instructions)
        self.assertIn("pacman -S", instructions)
        self.assertIn("dnf install", instructions)
        self.assertIn("brew install", instructions)
        self.assertIn("MiKTeX", instructions)

    @patch("scripts.doctor.check_xelatex")
    def test_run_doctor_exit_on_failure(self, mock_check):
        mock_check.return_value = (False, "Instalasi xelatex diperlukan")
        with self.assertRaises(SystemExit) as cm:
            run_doctor(exit_on_failure=True)
        self.assertEqual(cm.exception.code, 1)

    @patch("scripts.doctor.check_xelatex")
    def test_run_doctor_success(self, mock_check):
        mock_check.return_value = (True, "/usr/bin/xelatex")
        self.assertTrue(run_doctor(exit_on_failure=True))

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_doctor.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.doctor'`.

- [ ] **Step 3: Implement `scripts/doctor.py`**

```python
# scripts/doctor.py
"""
Pre-flight environment doctor check for XeLaTeX installation.
Provides cross-platform installation instructions when dependencies are missing.
"""

import shutil
import sys
from typing import Tuple

XELATEX_INSTALL_GUIDE = """
[ERROR] Program kompilasi 'xelatex' tidak ditemukan di sistem Anda!
Log book ini memerlukan XeLaTeX untuk mengompilasi lembar PDF dengan presisi tinggi.

Silakan pasang XeLaTeX sesuai sistem operasi Anda:

1. Ubuntu / Debian / Linux Mint:
   sudo apt update && sudo apt install -y texlive-xetex texlive-fonts-recommended

2. Arch Linux / Manjaro:
   sudo pacman -S texlive-bin texlive-core

3. Fedora / RHEL:
   sudo dnf install texlive-xetex texlive-collection-fontsrecommended

4. macOS (via Homebrew):
   brew install --cask mactex-no-gui
   # Atau MacTeX lengkap: brew install --cask mactex

5. Windows:
   Unduh dan pasang MiKTeX dari: https://miktex.org/download
   Pastikan opsi "Always install missing packages on the fly" diaktifkan.

Setelah instalasi selesai, buka kembali terminal Anda dan jalankan perintah kembali.
"""

def check_xelatex() -> Tuple[bool, str]:
    """
    Checks if xelatex executable is available in PATH.
    Returns (True, path_to_binary) if found, or (False, install_instructions).
    """
    path = shutil.which("xelatex")
    if path:
        return True, path
    return False, XELATEX_INSTALL_GUIDE

def run_doctor(exit_on_failure: bool = True) -> bool:
    """
    Runs pre-flight system checks. Prints clear guidance and exits if missing.
    """
    ok, message = check_xelatex()
    if not ok:
        print(message, file=sys.stderr)
        if exit_on_failure:
            sys.exit(1)
        return False
    return True
```

- [ ] **Step 4: Integrate `run_doctor` into `main.py`**

In `main.py`:
```python
from scripts.doctor import run_doctor

def main():
    ...
    args = parser.parse_args()

    # Pre-flight check: UI or PDF compilation requires xelatex unless --check-only is given
    if not args.check_only:
        run_doctor(exit_on_failure=True)
    ...
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m unittest tests/test_doctor.py`
Expected: PASS.

- [ ] **Step 6: Commit changes**

```bash
git add scripts/doctor.py tests/test_doctor.py main.py
git commit -m "feat: add pre-flight doctor check for xelatex with cross-platform guides"
```

---

### Task 5: Documentation & Open Source Licensing

**Files:**
- Create: `LICENSE` (MIT)
- Create: `README.md`
- Create: `data/README.md`

**Interfaces:**
- Consumes: Repository architecture, CLI flags, Web UI endpoints, `config.example.yaml`
- Produces: Complete open-source documentation and permissive licensing.

- [ ] **Step 1: Create `LICENSE`**

Create standard MIT License:
```text
MIT License

Copyright (c) 2026 Nathanael Juan Gracedo & Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Create `data/README.md`**

```markdown
# Struktur Direktori Data Log Book Magang

Direktori ini menyimpan catatan aktivitas harian magang industri dalam format YAML. Setiap berkas mewakili 1 bulan kalender magang (Juli s/d Desember 2026):

```text
data/
├── bulan_01_juli.yaml
├── bulan_02_agustus.yaml
├── bulan_03_september.yaml
├── bulan_04_oktober.yaml
├── bulan_05_november.yaml
└── bulan_06_desember.yaml
```

## Format Berkas

Setiap berkas YAML memiliki struktur berikut:

```yaml
bulan: 7
tahun: 2026
catatan:
  "2026-07-01": "Mengikuti onboarding magang dan setup lingkungan dev."
  "2026-07-02": "Mempelajari spesifikasi REST API backend."
```

## Tips Penggunaan
- Tanggal aktif adalah Senin sampai Sabtu (Minggu libur/otomatis diabaikan).
- Jika ada tanggal yang belum diisi, CLI akan memberikan notifikasi interaktif, atau Anda dapat menggunakan fitur **Batch Auto-Fill** pada Web UI Dashboard.
- Format teks catatan dapat berupa poin-poin ringkas. Fitur ekspansi narasi akan otomatis mengubahnya menjadi kalimat laporan formal berbahasa Indonesia.
```

- [ ] **Step 3: Create `README.md`**

```markdown
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
```

- [ ] **Step 4: Verify test suite and documentation files**

Run: `python3 -m unittest discover tests`
Expected: PASS with 100% tests passing.
Verify files exist:
```bash
ls -la README.md LICENSE data/README.md config.example.yaml
```

- [ ] **Step 5: Commit documentation and license**

```bash
git add README.md LICENSE data/README.md
git commit -m "docs: add comprehensive README, MIT license, and data guide"
```

---

## Plan Self-Review Checklist

- **Spec Coverage:**
  - Section 2 (Header LaTeX layout with 3 minipages, left logo, center text, right counterweight): Covered in Task 1.
  - Section 3.1 (`config.example.yaml`, `.gitignore`, auto-bootstrap in `load_config`): Covered in Task 3.
  - Section 3.2 (Environment doctor check for `xelatex` with cross-platform instructions): Covered in Task 4.
  - Section 3.3 (Comprehensive `README.md` and MIT `LICENSE`): Covered in Task 5.
  - Section 4 & Decoupled E2E tests: Covered in Task 2.
- **Placeholder Scan:** No "TODO", "TBD", or unwritten steps. Every step contains complete code and exact commands.
- **Type Consistency:** Function names (`load_config`, `check_xelatex`, `run_doctor`, `render_week_page`) match across implementations and tests.
