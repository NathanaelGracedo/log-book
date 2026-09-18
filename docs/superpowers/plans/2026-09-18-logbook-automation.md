# Logbook Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a command-line automation system in Python and XeLaTeX to generate official, weekly-paged PDF internship logbooks for Polinema at PT Naraya Telematika (July 1 – December 31, 2026) from structured YAML entries.

**Architecture:** A modular Python CLI loads user configuration and monthly YAML activity records, partitions the 2026 internship calendar into exactly 27 weeks (Monday–Saturday, 1 page per week), validates missing working days with an interactive terminal prompt, expands brief bullet points into formal Indonesian professional sentences with LaTeX escaping, and compiles 6 monthly PDF bundles plus 1 cumulative PDF via XeLaTeX.

**Tech Stack:** Python 3 (standard library: `datetime`, `zipfile`, `re`, `subprocess`, `argparse`, `unittest`), `PyYAML`, and `xelatex`.

## Global Constraints

- Internship Period: Wednesday, July 1, 2026 to Thursday, December 31, 2026 (`2026-07-01` to `2026-12-31`).
- Working schedule: 6 days per week (Monday to Saturday); Sunday is off / omitted.
- Working hours: Monday–Friday `08.00`–`16.00`; Saturday `08.00`–`14.00`.
- Calendar boundary: Week 1 starts on active day Wednesday July 1, 2026 (July 1–4, 4 days). Week 27 ends Thursday December 31, 2026 (Dec 28–31, 4 days).
- Page geometry: Exactly 1 week = 1 page A4. A 5-week monthly document must have exactly 5 pages; cumulative 27-week document must have exactly 27 pages.
- Header on each page: Polinema letterhead with official logos, institution typography, student identity, weekly table, and complete signature block (Mahasiswa, Dosen Pembimbing, Pembimbing Lapangan).
- Monthly output files:
  - `output/Logbook_01_Juli_2026.pdf` (Minggu 1–5)
  - `output/Logbook_02_Agustus_2026.pdf` (Minggu 6–9)
  - `output/Logbook_03_September_2026.pdf` (Minggu 10–14)
  - `output/Logbook_04_Oktober_2026.pdf` (Minggu 15–18)
  - `output/Logbook_05_November_2026.pdf` (Minggu 19–22)
  - `output/Logbook_06_Desember_2026.pdf` (Minggu 23–27)
  - `output/Logbook_Lengkap_Juli_Desember_2026.pdf` (Minggu 1–27)

---

### Task 1: Scaffolding, Asset Extraction, and Configuration Schema

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/extract_assets.py`
- Create: `config.yaml`
- Create: `tests/__init__.py`
- Create: `tests/test_extract_assets.py`

**Interfaces:**
- Consumes: `Log Book Template.docx` (word/media images).
- Produces:
  - `assets/polinema.png` and `assets/kemendikbud.jpg`
  - `extract_assets_from_docx(docx_path: str, assets_dir: str) -> dict[str, str]`
  - `config.yaml` containing mahasiswa, pembimbing, and pengaturan structures.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extract_assets.py
import unittest
import os
import yaml
from pathlib import Path
from scripts.extract_assets import extract_assets_from_docx

class TestExtractAssets(unittest.TestCase):
    def test_extract_assets(self):
        docx_path = "Log Book Template.docx"
        target_dir = "assets"
        extracted = extract_assets_from_docx(docx_path, target_dir)
        self.assertIn("polinema", extracted)
        self.assertTrue(os.path.exists(extracted["polinema"]))
        self.assertGreater(os.path.getsize(extracted["polinema"]), 0)

    def test_config_schema(self):
        self.assertTrue(os.path.exists("config.yaml"))
        with open("config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.assertIn("mahasiswa", cfg)
        self.assertIn("pembimbing", cfg)
        self.assertIn("pengaturan", cfg)
        self.assertEqual(cfg["mahasiswa"]["mitra"], "PT Naraya Telematika")
        self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin_jumat"]["masuk"], "08.00")
        self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin_jumat"]["pulang"], "16.00")
        self.assertEqual(cfg["pengaturan"]["jam_kerja"]["sabtu"]["pulang"], "14.00")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_extract_assets.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.extract_assets'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/__init__.py` and `tests/__init__.py` (empty files).

Create `scripts/extract_assets.py`:
```python
# scripts/extract_assets.py
import zipfile
import os
from pathlib import Path

def extract_assets_from_docx(docx_path: str = "Log Book Template.docx", assets_dir: str = "assets") -> dict[str, str]:
    """
    Extracts Polinema and Kemendikbud logo assets from the original docx template.
    """
    target_path = Path(assets_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    extracted = {}
    with zipfile.ZipFile(docx_path, 'r') as docx:
        for item in docx.namelist():
            if item == "word/media/image2.png":
                out_file = target_path / "polinema.png"
                with open(out_file, "wb") as f:
                    f.write(docx.read(item))
                extracted["polinema"] = str(out_file)
            elif item == "word/media/image1.jpg":
                out_file = target_path / "kemendikbud.jpg"
                with open(out_file, "wb") as f:
                    f.write(docx.read(item))
                extracted["kemendikbud"] = str(out_file)
                
    # If kemendikbud wasn't a distinct image in docx, copy polinema or fallback
    if "kemendikbud" not in extracted and "polinema" in extracted:
        fallback_kemen = target_path / "kemendikbud.jpg"
        with open(extracted["polinema"], "rb") as src, open(fallback_kemen, "wb") as dst:
            dst.write(src.read())
        extracted["kemendikbud"] = str(fallback_kemen)

    return extracted

if __name__ == "__main__":
    res = extract_assets_from_docx()
    print("Extracted assets:", res)
```

Create `config.yaml`:
```yaml
mahasiswa:
  nama: "Nama Mahasiswa"
  nim: "XXXXXXXXXX"
  prodi: "Sarjana Terapan Teknik Informatika"
  mitra: "PT Naraya Telematika"

pembimbing:
  dosen:
    nama: "Nama Dosen Pembimbing, M.Kom."
    nip: "198XXXXXXXXXXXX"
  lapangan:
    nama: "Nama Pembimbing Lapangan"
    nik: "ID/NIK Karyawan"

pengaturan:
  jam_kerja:
    senin_jumat:
      masuk: "08.00"
      pulang: "16.00"
    sabtu:
      masuk: "08.00"
      pulang: "14.00"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_extract_assets.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add config.yaml scripts/__init__.py scripts/extract_assets.py tests/__init__.py tests/test_extract_assets.py assets/
git commit -m "feat: scaffold assets extraction and config schema"
```

---

### Task 2: Calendar Engine & Month-Week Partitioning

**Files:**
- Create: `scripts/calendar_utils.py`
- Test: `tests/test_calendar_utils.py`

**Interfaces:**
- Consumes: Python `datetime`
- Produces:
  - `INDONESIAN_DAYS: dict[int, str]` (0: Senin, ..., 5: Sabtu)
  - `INDONESIAN_MONTHS: dict[int, str]` (7: Juli, ..., 12: Desember)
  - `MONTH_BUNDLE_WEEKS: dict[int, tuple[int, int]]` (1: (1, 5), 2: (6, 9), 3: (10, 14), 4: (15, 18), 5: (19, 22), 6: (23, 27))
  - `get_internship_calendar() -> list[dict]` (returns 27 weeks with daily schedule info)
  - `get_calendar_working_days(month_num: int | None = None) -> list[datetime.date]`
  - `get_month_bundle_weeks(bundle_index: int) -> list[dict]`
  - `get_yaml_filename_for_date(d: datetime.date) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_calendar_utils.py
import unittest
import datetime
from scripts.calendar_utils import (
    get_internship_calendar,
    get_calendar_working_days,
    get_month_bundle_weeks,
    get_yaml_filename_for_date,
    MONTH_BUNDLE_WEEKS
)

class TestCalendarUtils(unittest.TestCase):
    def test_total_weeks_and_bounds(self):
        weeks = get_internship_calendar()
        self.assertEqual(len(weeks), 27)
        # Week 1 starts 2026-07-01 (Wed) and ends 2026-07-04 (Sat) (4 days)
        w1 = weeks[0]
        self.assertEqual(w1["minggu_ke"], 1)
        self.assertEqual(len(w1["days"]), 4)
        self.assertEqual(w1["days"][0]["date"], datetime.date(2026, 7, 1))
        self.assertEqual(w1["days"][0]["hari"], "Rabu")
        self.assertEqual(w1["days"][0]["jam_masuk"], "08.00")
        self.assertEqual(w1["days"][0]["jam_pulang"], "16.00")
        self.assertEqual(w1["days"][3]["hari"], "Sabtu")
        self.assertEqual(w1["days"][3]["jam_pulang"], "14.00")

        # Week 27 ends 2026-12-31 (Thu) (4 days)
        w27 = weeks[26]
        self.assertEqual(w27["minggu_ke"], 27)
        self.assertEqual(len(w27["days"]), 4)
        self.assertEqual(w27["days"][-1]["date"], datetime.date(2026, 12, 31))
        self.assertEqual(w27["days"][-1]["hari"], "Kamis")

    def test_working_days_per_calendar_month(self):
        # Total active working days July - Dec: 158 days
        all_days = get_calendar_working_days(None)
        self.assertEqual(len(all_days), 158)
        # July: 31 days - 4 Sundays = 27 days
        july_days = get_calendar_working_days(7)
        self.assertEqual(len(july_days), 27)
        # August: 31 days - 5 Sundays = 26 days
        aug_days = get_calendar_working_days(8)
        self.assertEqual(len(aug_days), 26)

    def test_month_bundles(self):
        # Bundle 1 (July): Weeks 1-5 (5 weeks)
        b1 = get_month_bundle_weeks(1)
        self.assertEqual(len(b1), 5)
        self.assertEqual(b1[0]["minggu_ke"], 1)
        self.assertEqual(b1[-1]["minggu_ke"], 5)

        # Bundle 2 (August): Weeks 6-9 (4 weeks)
        b2 = get_month_bundle_weeks(2)
        self.assertEqual(len(b2), 4)
        self.assertEqual(b2[0]["minggu_ke"], 6)
        self.assertEqual(b2[-1]["minggu_ke"], 9)

    def test_yaml_filename_mapping(self):
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 7, 15)), "bulan_01_juli.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 8, 1)), "bulan_02_agustus.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 12, 31)), "bulan_06_desember.yaml")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.calendar_utils'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/calendar_utils.py`:
```python
# scripts/calendar_utils.py
import datetime

INDONESIAN_DAYS = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

INDONESIAN_MONTHS = {
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

# Mapping of month report index (1..6) to (start_week, end_week)
MONTH_BUNDLE_WEEKS = {
    1: (1, 5),    # Juli
    2: (6, 9),    # Agustus
    3: (10, 14),  # September
    4: (15, 18),  # Oktober
    5: (19, 22),  # November
    6: (23, 27),  # Desember
}

START_DATE = datetime.date(2026, 7, 1)
END_DATE = datetime.date(2026, 12, 31)

def format_indonesian_date(d: datetime.date) -> str:
    """Returns date in format: 1 Juli 2026"""
    month_name = INDONESIAN_MONTHS.get(d.month, str(d.month))
    return f"{d.day} {month_name} {d.year}"

def get_calendar_working_days(month_num: int | None = None) -> list[datetime.date]:
    """Returns all Monday-Saturday dates within the internship period or for a specific month (7..12)."""
    curr = START_DATE
    days = []
    while curr <= END_DATE:
        if curr.weekday() != 6:  # Skip Sunday
            if month_num is None or curr.month == month_num:
                days.append(curr)
        curr += datetime.timedelta(days=1)
    return days

def get_internship_calendar() -> list[dict]:
    """
    Partitions the internship period (2026-07-01 to 2026-12-31) into 27 weeks.
    Each week contains a list of day dictionaries:
      - date: datetime.date
      - date_str: "YYYY-MM-DD"
      - hari: "Senin", "Selasa", etc.
      - tanggal_str: "1 Juli 2026"
      - jam_masuk: "08.00"
      - jam_pulang: "16.00" (or "14.00" for Sabtu)
    """
    weeks = []
    current_days = []
    curr = START_DATE
    week_num = 1

    while curr <= END_DATE:
        if curr.weekday() != 6:
            hari = INDONESIAN_DAYS[curr.weekday()]
            jam_masuk = "08.00"
            jam_pulang = "14.00" if curr.weekday() == 5 else "16.00"
            day_info = {
                "date": curr,
                "date_str": curr.strftime("%Y-%m-%d"),
                "hari": hari,
                "tanggal_str": format_indonesian_date(curr),
                "jam_masuk": jam_masuk,
                "jam_pulang": jam_pulang,
            }
            current_days.append(day_info)

        # A week ends on Saturday or on the final day (Thursday Dec 31)
        if curr.weekday() == 5 or curr == END_DATE:
            if current_days:
                weeks.append({
                    "minggu_ke": week_num,
                    "days": current_days
                })
                week_num += 1
                current_days = []

        curr += datetime.timedelta(days=1)

    return weeks

def get_month_bundle_weeks(bundle_index: int) -> list[dict]:
    """Returns the list of weeks belonging to a specific monthly report bundle (1..6)."""
    if bundle_index not in MONTH_BUNDLE_WEEKS:
        raise ValueError(f"Bundle index must be between 1 and 6, got {bundle_index}")
    
    start_wk, end_wk = MONTH_BUNDLE_WEEKS[bundle_index]
    all_weeks = get_internship_calendar()
    return [w for w in all_weeks if start_wk <= w["minggu_ke"] <= end_wk]

def get_yaml_filename_for_date(d: datetime.date) -> str:
    """Maps a given date to its corresponding YAML filename based on month."""
    month_names = {
        7: "01_juli",
        8: "02_agustus",
        9: "03_september",
        10: "04_oktober",
        11: "05_november",
        12: "06_desember"
    }
    suffix = month_names.get(d.month)
    if not suffix:
        raise ValueError(f"Date {d} is outside the internship period (July-December 2026)")
    return f"bulan_{suffix}.yaml"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: PASS (`Ran 4 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add scripts/calendar_utils.py tests/test_calendar_utils.py
git commit -m "feat: add calendar engine and week-month partitioning"
```

---

### Task 3: Narrative Expansion & LaTeX Escaping Engine

**Files:**
- Create: `scripts/narrative_expander.py`
- Test: `tests/test_narrative_expander.py`

**Interfaces:**
- Consumes: string inputs (bullet points, activities)
- Produces:
  - `escape_latex(text: str) -> str` (escapes `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`)
  - `expand_narrative(bullet: str) -> str` (transforms concise bullet points into formal Indonesian professional sentences)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_narrative_expander.py
import unittest
from scripts.narrative_expander import escape_latex, expand_narrative

class TestNarrativeExpander(unittest.TestCase):
    def test_escape_latex(self):
        self.assertEqual(escape_latex("PT Naraya & Co."), r"PT Naraya \& Co.")
        self.assertEqual(escape_latex("Progress 100%"), r"Progress 100\%")
        self.assertEqual(escape_latex("user_id & item_id"), r"user\_id \& item\_id")
        self.assertEqual(escape_latex("$100 #hashtag {code}"), r"\$100 \#hashtag \{code\}")
        self.assertEqual(escape_latex(r"c:\path\to\file"), r"c:\textbackslash{}path\textbackslash{}to\textbackslash{}file")

    def test_expand_narrative_rules(self):
        # Rule: onboarding
        res1 = expand_narrative("onboarding magang dan setup laptop")
        self.assertIn("onboarding", res1.lower())
        self.assertTrue(res1.endswith("."))
        self.assertTrue(res1[0].isupper())

        # Rule: meeting
        res2 = expand_narrative("meeting mingguan tim dan review tiket sprint")
        self.assertTrue(res2.startswith("Menghadiri rapat koordinasi tim"))
        self.assertTrue(res2.endswith("."))

        # Rule: existing formal sentence preserved
        formal = "Mengembangkan antarmuka pengguna dashboard analitik menggunakan Tailwind CSS."
        self.assertEqual(expand_narrative(formal), formal)

        # Rule: empty string
        self.assertEqual(expand_narrative(""), "")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_narrative_expander.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.narrative_expander'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/narrative_expander.py`:
```python
# scripts/narrative_expander.py
import re

def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters in string.
    Special chars: \ & % $ # _ { } ~ ^
    """
    if not text:
        return ""
    
    # \ must be replaced first to avoid escaping backslashes from other escapes
    text = text.replace('\\', r'\textbackslash{}')
    
    replacements = [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for orig, rep in replacements:
        text = text.replace(orig, rep)
        
    return text

EXPANSION_RULES = [
    (r"^(?:onboarding|orientasi)\b(.*)", r"Mengikuti kegiatan onboarding magang dan pengenalan lingkungan kerja industri\1."),
    (r"^(?:setup laptop|setup environment|setup env|setup dev)\b(.*)", r"Melakukan instalasi dan konfigurasi lingkungan pengembangan perangkat lunak pada perangkat kerja\1."),
    (r"^(?:pelajari|belajar|analisis)\b(.*)", r"Mempelajari dan menganalisis arsitektur sistem serta dokumentasi proyek\1."),
    (r"^(?:meeting|rapat|daily standup|standup)\b(.*)", r"Menghadiri rapat koordinasi tim dan sinkronisasi tugas harian\1."),
    (r"^(?:code review|review code|review)\b(.*)", r"Melakukan peninjauan kembali kode program (code review) dan diskusi implementasi\1."),
    (r"^(?:eksplorasi|riset)\b(.*)", r"Melakukan eksplorasi teknis dan riset implementasi terhadap\1."),
    (r"^(?:implementasi|coding|develop|buat|membuat)\b(.*)", r"Mengembangkan dan mengimplementasikan modul fitur\1."),
    (r"^(?:testing|uji|pengujian)\b(.*)", r"Melakukan pengujian sistem serta verifikasi fungsionalitas fitur\1."),
    (r"^(?:bugfix|fixing|perbaikan bug|perbaikan)\b(.*)", r"Melakukan penelusuran masalah dan perbaikan kendala teknis (bug fixing)\1."),
    (r"^(?:dokumentasi|susun dokumen)\b(.*)", r"Menyusun dan memperbarui dokumentasi teknis kegiatan magang\1."),
]

def expand_narrative(bullet: str) -> str:
    """
    Expands a concise bullet point into a formal Indonesian professional sentence.
    If the sentence is already formal (starts with capital and ends with period), returns it normalized.
    """
    if not bullet or not bullet.strip():
        return ""
    
    clean = bullet.strip().lstrip("-*•1234567890. ").strip()
    if not clean:
        return ""

    # Check if already a formal complete sentence
    if clean[0].isupper() and clean.endswith((".", "!", "?")):
        return clean

    # Attempt pattern matches
    lower_clean = clean.lower()
    for pattern, template in EXPANSION_RULES:
        m = re.search(pattern, lower_clean)
        if m:
            tail = clean[m.end(0) - len(m.group(1)):].strip()
            expanded = re.sub(pattern, template, lower_clean)
            if tail:
                # Capitalize first letter and ensure ending period
                expanded = expanded.rstrip(".") + " " + tail
            expanded = expanded.strip().rstrip(".") + "."
            return expanded[0].upper() + expanded[1:]

    # Fallback: capitalize first letter, prepend "Melakukan " if starts with lowercase verb/noun, and add period
    if not clean[0].isupper():
        clean = "Melakukan " + clean
    clean = clean.rstrip(".") + "."
    return clean[0].upper() + clean[1:]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_narrative_expander.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add scripts/narrative_expander.py tests/test_narrative_expander.py
git commit -m "feat: add narrative expander and latex escaping"
```

---

### Task 4: Data Manager & Interactive Missing Date Validator

**Files:**
- Create: `scripts/data_manager.py`
- Test: `tests/test_data_manager.py`

**Interfaces:**
- Consumes: `config.yaml`, `data/bulan_XX.yaml` files.
- Produces:
  - `init_data_files(data_dir: str) -> None`
  - `load_all_notes(data_dir: str) -> dict[str, str]`
  - `save_note_to_month(date_val: datetime.date, note: str, data_dir: str) -> None`
  - `check_missing_dates(month_bundle_idx: int | None = None, data_dir: str = "data") -> list[datetime.date]`
  - `prompt_fill_missing(missing_dates: list[datetime.date], input_func=input, print_func=print, data_dir: str = "data") -> int`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_data_manager.py
import unittest
import tempfile
import os
import datetime
from pathlib import Path
import yaml
from scripts.data_manager import (
    init_data_files,
    load_all_notes,
    save_note_to_month,
    check_missing_dates,
    prompt_fill_missing
)

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = self.temp_dir.name
        init_data_files(self.data_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_creates_6_files(self):
        files = os.listdir(self.data_dir)
        self.assertEqual(len([f for f in files if f.endswith(".yaml")]), 6)

    def test_save_and_load_note(self):
        d = datetime.date(2026, 7, 1)
        save_note_to_month(d, "onboarding dan setup dev", self.data_dir)
        notes = load_all_notes(self.data_dir)
        self.assertIn("2026-07-01", notes)
        self.assertEqual(notes["2026-07-01"], "onboarding dan setup dev")

    def test_missing_dates_detection(self):
        missing = check_missing_dates(1, self.data_dir)
        # Week 1-5 has total working days in July plus Aug 1st
        self.assertGreater(len(missing), 0)
        # Fill one day and verify missing decreased by 1
        d = missing[0]
        save_note_to_month(d, "kegiatan hari ini", self.data_dir)
        missing_after = check_missing_dates(1, self.data_dir)
        self.assertEqual(len(missing_after), len(missing) - 1)

    def test_prompt_fill_missing(self):
        missing = [datetime.date(2026, 7, 1), datetime.date(2026, 7, 2)]
        inputs = iter(["onboarding selesai", ""])  # fills first, skips second
        prompts = []
        filled = prompt_fill_missing(
            missing,
            input_func=lambda prompt: next(inputs),
            print_func=lambda msg: prompts.append(msg),
            data_dir=self.data_dir
        )
        self.assertEqual(filled, 1)
        notes = load_all_notes(self.data_dir)
        self.assertIn("2026-07-01", notes)
        self.assertNotIn("2026-07-02", notes)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_data_manager.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.data_manager'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/data_manager.py`:
```python
# scripts/data_manager.py
import os
from pathlib import Path
import datetime
import yaml
from scripts.calendar_utils import (
    get_yaml_filename_for_date,
    get_month_bundle_weeks,
    get_internship_calendar,
    format_indonesian_date,
    INDONESIAN_DAYS
)

MONTH_FILE_TEMPLATES = [
    (7, 2026, "bulan_01_juli.yaml"),
    (8, 2026, "bulan_02_agustus.yaml"),
    (9, 2026, "bulan_03_september.yaml"),
    (10, 2026, "bulan_04_oktober.yaml"),
    (11, 2026, "bulan_05_november.yaml"),
    (12, 2026, "bulan_06_desember.yaml"),
]

def init_data_files(data_dir: str = "data") -> None:
    """Ensures that all 6 monthly YAML data files exist with their skeleton headers."""
    target_path = Path(data_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    for bulan, tahun, filename in MONTH_FILE_TEMPLATES:
        file_path = target_path / filename
        if not file_path.exists():
            content = {
                "bulan": bulan,
                "tahun": tahun,
                "catatan": {}
            }
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, allow_unicode=True, default_flow_style=False)

def load_all_notes(data_dir: str = "data") -> dict[str, str]:
    """Loads and merges all daily activity records from all monthly yaml files."""
    init_data_files(data_dir)
    target_path = Path(data_dir)
    merged_notes = {}

    for _, _, filename in MONTH_FILE_TEMPLATES:
        file_path = target_path / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                catatan = data.get("catatan") or {}
                for k, v in catatan.items():
                    if v and str(v).strip():
                        merged_notes[str(k)] = str(v).strip()

    return merged_notes

def save_note_to_month(date_val: datetime.date, note: str, data_dir: str = "data") -> None:
    """Saves or updates a daily note in the appropriate monthly YAML file."""
    filename = get_yaml_filename_for_date(date_val)
    file_path = Path(data_dir) / filename
    
    data = {}
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    
    if "catatan" not in data or data["catatan"] is None:
        data["catatan"] = {}
        
    date_key = date_val.strftime("%Y-%m-%d")
    data["catatan"][date_key] = note.strip()
    
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=True)

def check_missing_dates(month_bundle_idx: int | None = None, data_dir: str = "data") -> list[datetime.date]:
    """
    Finds missing dates with no note recorded.
    If month_bundle_idx (1..6) is provided, checks only weeks belonging to that bundle.
    If None, checks all 27 weeks.
    """
    if month_bundle_idx is not None:
        weeks = get_month_bundle_weeks(month_bundle_idx)
    else:
        weeks = get_internship_calendar()

    existing_notes = load_all_notes(data_dir)
    missing = []

    for w in weeks:
        for day in w["days"]:
            d_str = day["date_str"]
            if d_str not in existing_notes:
                missing.append(day["date"])

    return missing

def prompt_fill_missing(
    missing_dates: list[datetime.date],
    input_func=input,
    print_func=print,
    data_dir: str = "data"
) -> int:
    """Interactively prompts the user in the CLI to fill missing activity entries."""
    if not missing_dates:
        return 0

    print_func(f"\n[INFO] Ditemukan {len(missing_dates)} hari kerja aktif yang belum memiliki catatan kegiatan.")
    print_func("Ketik catatan kegiatan, tekan [Enter] untuk lewati, atau ketik 'q' untuk keluar pengisian.\n")

    filled_count = 0
    for d in missing_dates:
        hari_name = INDONESIAN_DAYS[d.weekday()]
        d_fmt = format_indonesian_date(d)
        prompt_text = f"[{d.strftime('%Y-%m-%d')} - {hari_name}, {d_fmt}] Kegiatan: "
        
        try:
            val = input_func(prompt_text)
        except (KeyboardInterrupt, EOFError):
            print_func("\nPengisian dibatalkan oleh pengguna.")
            break

        if val is None:
            break
        val = val.strip()
        if val.lower() == "q":
            print_func("Keluar dari pengisian interaktif.")
            break
        if val:
            save_note_to_month(d, val, data_dir)
            filled_count += 1
            print_func(f"  -> Tersimpan untuk {d.strftime('%Y-%m-%d')}.")

    return filled_count
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_data_manager.py`
Expected: PASS (`Ran 4 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add scripts/data_manager.py tests/test_data_manager.py
git commit -m "feat: add data manager and interactive missing date validator"
```

---

### Task 5: Master LaTeX Template & Document Generator

**Files:**
- Create: `templates/logbook_template.tex`
- Create: `scripts/latex_builder.py`
- Test: `tests/test_latex_builder.py`

**Interfaces:**
- Consumes: weeks data, expanded notes, `config.yaml`, asset paths.
- Produces:
  - `templates/logbook_template.tex`
  - `generate_latex_document(weeks: list[dict], notes_map: dict[str, str], config: dict, assets_dir: str) -> str`
  - `compile_pdf(latex_code: str, output_pdf_path: str, work_dir: str | None = None) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_latex_builder.py
import unittest
import os
import tempfile
import datetime
from pathlib import Path
from scripts.latex_builder import generate_latex_document, compile_pdf

class TestLatexBuilder(unittest.TestCase):
    def setUp(self):
        self.config = {
            "mahasiswa": {
                "nama": "Budi Santoso",
                "nim": "2241720001",
                "prodi": "Sarjana Terapan Teknik Informatika",
                "mitra": "PT Naraya Telematika"
            },
            "pembimbing": {
                "dosen": {"nama": "Dr. Ir. Pembimbing, M.Kom.", "nip": "198001012005011001"},
                "lapangan": {"nama": "Senior Engineer", "nik": "EMP-1002"}
            }
        }
        self.weeks = [{
            "minggu_ke": 1,
            "days": [
                {
                    "date": datetime.date(2026, 7, 1),
                    "date_str": "2026-07-01",
                    "hari": "Rabu",
                    "tanggal_str": "1 Juli 2026",
                    "jam_masuk": "08.00",
                    "jam_pulang": "16.00"
                }
            ]
        }]
        self.notes_map = {
            "2026-07-01": "Mengikuti onboarding & instalasi software kerja."
        }

    def test_generate_latex_contains_required_fields(self):
        latex = generate_latex_document(self.weeks, self.notes_map, self.config)
        self.assertIn("Budi Santoso", latex)
        self.assertIn("2241720001", latex)
        self.assertIn("PT Naraya Telematika", latex)
        self.assertIn("Mengikuti onboarding \\& instalasi software kerja.", latex)
        self.assertIn("LOG BOOK KEGIATAN", latex)
        self.assertIn(r"\clearpage", latex)

    def test_compile_pdf(self):
        latex = generate_latex_document(self.weeks, self.notes_map, self.config)
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = os.path.join(tmp_dir, "test_output.pdf")
            success = compile_pdf(latex, out_pdf)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_pdf))
            self.assertGreater(os.path.getsize(out_pdf), 0)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.latex_builder'`

- [ ] **Step 3: Write minimal implementation**

Create `templates/logbook_template.tex`:
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[a4paper, top=1.2cm, bottom=1.2cm, left=2.0cm, right=1.5cm, footskip=0.7cm]{geometry}
\usepackage{fontspec}
\setmainfont{Liberation Serif}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{lastpage}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[R]{\small Halaman \thepage\ dari \pageref{LastPage}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}

\begin{document}

%CONTENT_BLOCK%

\end{document}
```

Create `scripts/latex_builder.py`:
```python
# scripts/latex_builder.py
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from scripts.narrative_expander import escape_latex, expand_narrative

def render_week_page(week_data: dict, notes_map: dict[str, str], config: dict, assets_dir: str = "assets") -> str:
    """Renders a single weekly page (exact 1 page A4)."""
    mhs = config.get("mahasiswa", {})
    pemb = config.get("pembimbing", {})
    dosen = pemb.get("dosen", {})
    lapangan = pemb.get("lapangan", {})

    nama_mhs = escape_latex(mhs.get("nama", ""))
    nim_mhs = escape_latex(mhs.get("nim", ""))
    prodi_mhs = escape_latex(mhs.get("prodi", "Sarjana Terapan Teknik Informatika"))
    mitra_mhs = escape_latex(mhs.get("mitra", "PT Naraya Telematika"))

    nama_dosen = escape_latex(dosen.get("nama", "...................................."))
    nip_dosen = escape_latex(dosen.get("nip", "...................................."))
    nama_lapangan = escape_latex(lapangan.get("nama", "...................................."))
    nik_lapangan = escape_latex(lapangan.get("nik", "...................................."))

    polinema_logo = os.path.abspath(os.path.join(assets_dir, "polinema.png"))
    kemendikbud_logo = os.path.abspath(os.path.join(assets_dir, "kemendikbud.jpg"))

    # Kop surat
    has_polinema = os.path.exists(polinema_logo)
    has_kemen = os.path.exists(kemendikbud_logo)

    logo_left_tex = f"\\includegraphics[height=2.0cm]{{{polinema_logo}}}" if has_polinema else ""
    logo_right_tex = f"\\includegraphics[height=2.0cm]{{{kemendikbud_logo}}}" if has_kemen else ""

    kop_tex = f"""
\\begin{{minipage}}[c]{{0.14\\textwidth}}
\\centering
{logo_left_tex}
\\end{{minipage}}%
\\begin{{minipage}}[c]{{0.72\\textwidth}}
\\centering
{{\\fontsize{{9.5pt}}{{11pt}}\\selectfont \\textbf{{KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI}}\\\\}}
{{\\fontsize{{11pt}}{{13pt}}\\selectfont \\textbf{{POLITEKNIK NEGERI MALANG}}\\\\}}
{{\\fontsize{{10pt}}{{12pt}}\\selectfont \\textbf{{JURUSAN TEKNOLOGI INFORMASI}}\\\\}}
{{\\fontsize{{8pt}}{{9.5pt}}\\selectfont Jalan Soekarno Hatta Nomor 9, Jatimulyo, Lowokwaru, Malang 65141\\\\}}
{{\\fontsize{{8pt}}{{9.5pt}}\\selectfont Telepon (0341) 404424, 404425, Faksimile (0341) 404420\\\\}}
{{\\fontsize{{8pt}}{{9.5pt}}\\selectfont Laman www.polinema.ac.id\\\\}}
\\end{{minipage}}%
\\begin{{minipage}}[c]{{0.14\\textwidth}}
\\centering
{logo_right_tex}
\\end{{minipage}}

\\vspace{{2pt}}
\\hrule height 1.5pt
\\vspace{{1pt}}
\\hrule height 0.5pt
\\vspace{{0.3cm}}
"""

    title_tex = """
\\begin{center}
{\\fontsize{12pt}{14pt}\\selectfont \\textbf{LOG BOOK KEGIATAN}\\\\}
{\\fontsize{12pt}{14pt}\\selectfont \\textbf{PROGRAM MAGANG INDUSTRI}\\\\}
\\end{center}
\\vspace{0.2cm}
"""

    identitas_tex = f"""
\\begin{{tabular}}{{@{{}}p{{3.8cm}} p{{0.2cm}} p{{12.5cm}}@{{}}}}
Nama Mahasiswa & : & {nama_mhs} \\\\
NIM & : & {nim_mhs} \\\\
Program Studi & : & {prodi_mhs} \\\\
Nama Mitra Industri & : & {mitra_mhs} \\\\
\\end{{tabular}}
\\vspace{{0.3cm}}
"""

    # Rows for the table
    rows_tex = []
    for d in week_data["days"]:
        d_str = d["date_str"]
        hari_tgl = f"{d['hari']}, {d['tanggal_str']}"
        raw_note = notes_map.get(d_str, "")
        expanded = expand_narrative(raw_note)
        escaped_note = escape_latex(expanded)
        row = f"\\textbf{{{hari_tgl}}} & {d['jam_masuk']} & {d['jam_pulang']} & {escaped_note} \\\\"
        rows_tex.append(row)

    table_rows = "\n\\hline\n".join(rows_tex)

    table_tex = f"""
\\renewcommand{{\\arraystretch}}{{1.35}}
\\begin{{tabularx}}{{\\textwidth}}{{|p{{4.2cm}}|c|c|X|}}
\\hline
\\textbf{{Hari, Tanggal}} & \\textbf{{Jam Masuk}} & \\textbf{{Jam Pulang}} & \\textbf{{Kegiatan}} \\\\
\\hline
{table_rows}
\\hline
\\end{{tabularx}}
\\vspace{{0.4cm}}
"""

    ttd_tex = f"""
\\noindent
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}X c X@{{}}}}
Mahasiswa, & & Mengetahui, \\\\
& & Dosen Pembimbing, \\\\
\\vspace{{1.6cm}} & & \\vspace{{1.6cm}} \\\\
\\textbf{{{nama_mhs}}} & & \\textbf{{{nama_dosen}}} \\\\
NIM. {nim_mhs} & & NIP. {nip_dosen} \\\\
\\end{{tabularx}}

\\vspace{{0.3cm}}
\\noindent
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}X c X@{{}}}}
& & Pembimbing Lapangan, \\\\
& & \\vspace{{1.6cm}} \\\\
& & \\textbf{{{nama_lapangan}}} \\\\
& & NIK. {nik_lapangan} \\\\
\\end{{tabularx}}
"""

    return kop_tex + title_tex + identitas_tex + table_tex + ttd_tex

def generate_latex_document(
    weeks: list[dict],
    notes_map: dict[str, str],
    config: dict,
    assets_dir: str = "assets",
    template_path: str = "templates/logbook_template.tex"
) -> str:
    """Renders all weekly pages into the complete LaTeX document."""
    page_blocks = []
    for w in weeks:
        page_content = render_week_page(w, notes_map, config, assets_dir)
        page_blocks.append(page_content)

    joined_content = "\n\\clearpage\n".join(page_blocks)

    with open(template_path, "r", encoding="utf-8") as f:
        master_template = f.read()

    return master_template.replace("%CONTENT_BLOCK%", joined_content)

def compile_pdf(latex_code: str, output_pdf_path: str, work_dir: str | None = None) -> bool:
    """Compiles LaTeX code using XeLaTeX into the target output PDF path."""
    clean_tmp = False
    if work_dir is None:
        work_dir = tempfile.mkdtemp(prefix="logbook_xelatex_")
        clean_tmp = True

    try:
        tex_path = os.path.join(work_dir, "document.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # Run xelatex twice to resolve LastPage references
        for _ in range(2):
            cmd = [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={work_dir}",
                tex_path
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"XeLaTeX compilation failed with exit code {proc.returncode}:\n{proc.stdout[-1500:]}")

        built_pdf = os.path.join(work_dir, "document.pdf")
        if not os.path.exists(built_pdf):
            raise FileNotFoundError("Output PDF was not created by XeLaTeX.")

        target_dir = os.path.dirname(os.path.abspath(output_pdf_path))
        os.makedirs(target_dir, exist_ok=True)
        shutil.copyfile(built_pdf, output_pdf_path)
        return True

    finally:
        if clean_tmp and os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add templates/logbook_template.tex scripts/latex_builder.py tests/test_latex_builder.py
git commit -m "feat: add latex template and xelatex builder"
```

---

### Task 6: CLI Orchestrator & End-to-End Build Pipeline

**Files:**
- Create: `main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: CLI arguments (`--month`, `--all`, `--check-only`, `--non-interactive`, `--cumulative-only`)
- Produces:
  - Generated PDFs in `output/`:
    - `output/Logbook_01_Juli_2026.pdf` .. `output/Logbook_06_Desember_2026.pdf`
    - `output/Logbook_Lengkap_Juli_Desember_2026.pdf`
  - Exit code 0 on success, informative status messages.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_main.py
import unittest
import os
import subprocess
import yaml

class TestMainCLI(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run(["python3", "main.py", "--help"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--month", res.stdout)
        self.assertIn("--check-only", res.stdout)

    def test_check_only_flag(self):
        res = subprocess.run(["python3", "main.py", "--check-only", "--non-interactive"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_main.py`
Expected: FAIL with `FileNotFoundError` or exit code 1 (`main.py` not created yet).

- [ ] **Step 3: Write minimal implementation**

Create `main.py`:
```python
# main.py
import argparse
import os
import sys
import yaml
from pathlib import Path
from scripts.extract_assets import extract_assets_from_docx
from scripts.calendar_utils import (
    get_internship_calendar,
    get_month_bundle_weeks,
    MONTH_BUNDLE_WEEKS,
    INDONESIAN_MONTHS
)
from scripts.data_manager import (
    init_data_files,
    load_all_notes,
    check_missing_dates,
    prompt_fill_missing
)
from scripts.latex_builder import generate_latex_document, compile_pdf

OUTPUT_MONTHLY_FILENAMES = {
    1: "Logbook_01_Juli_2026.pdf",
    2: "Logbook_02_Agustus_2026.pdf",
    3: "Logbook_03_September_2026.pdf",
    4: "Logbook_04_Oktober_2026.pdf",
    5: "Logbook_05_November_2026.pdf",
    6: "Logbook_06_Desember_2026.pdf",
}
CUMULATIVE_FILENAME = "Logbook_Lengkap_Juli_Desember_2026.pdf"

def load_config(config_path: str = "config.yaml") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Konfigurasi {config_path} tidak ditemukan.")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ensure_assets():
    assets_dir = "assets"
    polinema_png = os.path.join(assets_dir, "polinema.png")
    if not os.path.exists(polinema_png) and os.path.exists("Log Book Template.docx"):
        print("[INFO] Mengekstrak logo dari 'Log Book Template.docx'...")
        extract_assets_from_docx("Log Book Template.docx", assets_dir)

def build_pdf_bundle(weeks: list[dict], notes_map: dict[str, str], config: dict, out_name: str) -> str:
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out_pdf = os.path.join(output_dir, out_name)
    print(f"[BUILD] Men-generate {out_name} ({len(weeks)} halaman)...")
    latex_doc = generate_latex_document(weeks, notes_map, config)
    compile_pdf(latex_doc, out_pdf)
    print(f"[OK] Berhasil: {out_pdf}")
    return out_pdf

def main():
    parser = argparse.ArgumentParser(description="Log Book Polinema Automation Generator")
    parser.add_argument("-m", "--month", type=int, choices=range(1, 7), help="Pilih bulan ke-1 s/d 6 untuk digenerate")
    parser.add_argument("--all", action="store_true", help="Generate semua 6 bulan + 1 file kumulatif")
    parser.add_argument("--cumulative-only", action="store_true", help="Hanya generate file PDF kumulatif")
    parser.add_argument("--check-only", action="store_true", help="Hanya cek tanggal kosong tanpa kompilasi PDF")
    parser.add_argument("--non-interactive", action="store_true", help="Nonaktifkan prompt interaktif untuk tanggal kosong")
    args = parser.parse_args()

    ensure_assets()
    init_data_files("data")
    config = load_config("config.yaml")

    # Determine which target bundles to process
    if args.month:
        target_months = [args.month]
    elif args.cumulative_only:
        target_months = []
    else:
        target_months = list(range(1, 7))

    # Check missing dates
    if args.cumulative_only or args.all or (not args.month):
        missing = check_missing_dates(None, "data")
    else:
        missing = check_missing_dates(args.month, "data")

    if missing:
        if args.non_interactive:
            print(f"[PERINGATAN] Ditemukan {len(missing)} tanggal aktif yang belum memiliki catatan kegiatan.")
        else:
            prompt_fill_missing(missing, data_dir="data")

    if args.check_only:
        print("[INFO] Pemeriksaan tanggal selesai.")
        sys.exit(0)

    # Reload notes after possible interactive fills
    notes_map = load_all_notes("data")

    generated = []

    # Build targeted monthly PDFs
    if not args.cumulative_only:
        for m_idx in target_months:
            weeks = get_month_bundle_weeks(m_idx)
            out_name = OUTPUT_MONTHLY_FILENAMES[m_idx]
            pdf_path = build_pdf_bundle(weeks, notes_map, config, out_name)
            generated.append(pdf_path)

    # Build cumulative PDF if requested or default
    if args.all or args.cumulative_only or (not args.month and not target_months):
        all_weeks = get_internship_calendar()
        pdf_path = build_pdf_bundle(all_weeks, notes_map, config, CUMULATIVE_FILENAME)
        generated.append(pdf_path)

    print("\n[SELESAI] Ringkasan berkas PDF yang dihasilkan:")
    for path in generated:
        print(f"  - {path}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_main.py`
Expected: PASS (`Ran 2 tests in ... OK`)

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement CLI orchestrator and build pipeline"
```

---

### Task 7: Sample Data Fixtures, Page Verification, and Full Build

**Files:**
- Modify: `data/bulan_01_juli.yaml`
- Modify: `data/bulan_02_agustus.yaml` .. `data/bulan_06_desember.yaml`
- Create: `tests/test_e2e.py`

**Interfaces:**
- Consumes: all project scripts and templates
- Produces:
  - Verified realistic daily log entries for July 2026.
  - End-to-end test verifying compilation of July report and checking strict 1-week-per-page rule.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_e2e.py
import unittest
import os
import subprocess

class TestEndToEndBuild(unittest.TestCase):
    def test_build_month_1(self):
        # Build month 1
        res = subprocess.run(["python3", "main.py", "--month", "1", "--non-interactive"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        # Verify page count: Month 1 has Weeks 1..5 -> exactly 5 pages
        pdfinfo_res = subprocess.run(["pdfinfo", pdf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if pdfinfo_res.returncode == 0:
            lines = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
            if lines:
                pages = int(lines[0].split(":")[1].strip())
                self.assertEqual(pages, 5, f"Expected exactly 5 pages for Month 1, got {pages}")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_e2e.py`
Expected: FAIL (pdf not generated yet or missing data).

- [ ] **Step 3: Populate sample data and ensure clean compilation**

Populate `data/bulan_01_juli.yaml` with realistic industry internship notes:
```yaml
bulan: 7
tahun: 2026
catatan:
  "2026-07-01": "onboarding magang industri dan pengenalan tim rekayasa perangkat lunak"
  "2026-07-02": "setup laptop dev, konfigurasi docker dan akses repositori git"
  "2026-07-03": "pelajari arsitektur sistem backend klien dan spesifikasi api"
  "2026-07-04": "eksplorasi database postgresql modul manajemen pengguna"
  "2026-07-06": "meeting mingguan sprint planning dan pembagian tiket tugas"
  "2026-07-07": "implementasi endpoint autentikasi jwt pada modul login"
  "2026-07-08": "coding validasi input form dan sanitasi data payload"
  "2026-07-09": "testing integrasi endpoint autentikasi menggunakan postman"
  "2026-07-10": "bugfix penanganan token expired pada middleware otorisasi"
  "2026-07-11": "dokumentasi teknis alur autentikasi pada wiki repositori"
  "2026-07-13": "meeting koordinasi tim backend mengenai skema relasi database"
  "2026-07-14": "implementasi modul manajemen data master pengguna"
  "2026-07-15": "coding logic filter dan pagination data tabel transaksi"
  "2026-07-16": "testing unit test service layer modul manajemen pengguna"
  "2026-07-17": "code review bersama pembimbing lapangan untuk merge request modul auth"
  "2026-07-18": "perbaikan feedback review dan refactoring fungsi helper"
  "2026-07-20": "meeting mingguan tim, review progress sprint berjalan"
  "2026-07-21": "eksplorasi integrasi message broker rabbitmq untuk event logging"
  "2026-07-22": "implementasi producer event logging pada transaksi layanan"
  "2026-07-23": "coding consumer worker event logging dan persistensi database"
  "2026-07-24": "testing beban message throughput dan verifikasi error handling"
  "2026-07-25": "dokumentasi skema antrian pesan dan konfigurasi cluster lokal"
  "2026-07-27": "meeting sinkronisasi sprint review dan demo fitur internal"
  "2026-07-28": "implementasi fitur ekspor data laporan transaksi ke format excel"
  "2026-07-29": "coding optimasi query sql untuk agregasi laporan bulanan"
  "2026-07-30": "testing performa database query dan indexing kolom transaksi"
  "2026-07-31": "code review modul laporan dan persiapan deployment staging"
```

Populate `data/bulan_02_agustus.yaml` with Aug 1st note (part of Week 5):
```yaml
bulan: 8
tahun: 2026
catatan:
  "2026-08-01": "evaluasi akhir pekan bersama pembimbing lapangan mengenai progress bulan juli"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_e2e.py`
Expected: PASS (`Ran 1 test in ... OK`)

Run full test suite:
Run: `python3 -m unittest discover tests`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add data/bulan_01_juli.yaml data/bulan_02_agustus.yaml tests/test_e2e.py
git commit -m "feat: populate sample data fixtures and verify e2e build"
```

---

## Self-Review

1. **Spec Coverage:**
   - 6 working days (Mon–Sat, Sun off): Covered in `scripts/calendar_utils.py` (`weekday() != 6`).
   - Work hours (Senin-Jumat 08.00–16.00, Sabtu 08.00–14.00): Covered in `calendar_utils.py`.
   - Date span 1 Juli 2026 – 31 Desember 2026: Covered in `calendar_utils.py`.
   - Minggu 1 begins Wed 1 Juli – Sat 4 Juli (4 days): Covered in `calendar_utils.py`.
   - Missing date interactive reminder: Covered in `scripts/data_manager.py` (`prompt_fill_missing`) and `main.py`.
   - Hybrid narrative expansion & LaTeX escaping: Covered in `scripts/narrative_expander.py`.
   - Strict 1 week = 1 page A4 layout: Covered in `templates/logbook_template.tex` and tested in `test_e2e.py`.
   - Letterhead Kop Polinema + student identity + signature block: Covered in `scripts/latex_builder.py`.
   - 6 monthly PDFs + 1 cumulative PDF bundling: Covered in `main.py`.

2. **Placeholder Scan:**
   - No `TODO`, `TBD`, or "implement later".
   - All code snippets, tests, commands, and schemas are fully specified and concrete.

3. **Type and Interface Consistency:**
   - Function names and signatures (`get_internship_calendar`, `get_month_bundle_weeks`, `escape_latex`, `expand_narrative`, `init_data_files`, `load_all_notes`, `save_note_to_month`, `generate_latex_document`, `compile_pdf`) match identically across modules and tests.
