# Dynamic Period, Attendance Status, and Signature Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement fully dynamic internship period dates, flexible 5-day (Mon–Fri) or 6-day (Mon–Sat) working schedules, attendance status tracking (`Hadir`, `Izin`, `Sakit`, `Cuti`, `Libur Nasional`) with red-colored narrative text and `-` work hours, a modernized 2-tier signature layout without NIM/NIP/NIK labels, and an interactive setup wizard across both CLI and Web UI.

**Architecture:** Extend `scripts/calendar_utils.py` to calculate date ranges and working days dynamically based on `config.yaml` (`periode` and `pengaturan.hari_kerja`), grouping weeks into dynamic calendar month bundles. Update `scripts/data_manager.py` to support structured attendance status dictionaries alongside legacy string notes. Enhance `scripts/latex_builder.py` and `templates/logbook_template.tex` using `\usepackage{xcolor}` to render attendance status in red text, set hours to `-`, and generate the streamlined 2-tier signature block. Finally, upgrade `main.py` with an interactive terminal setup wizard and expand `web/` (FastAPI backend + Bento Grid SPA frontend) to allow configuring date ranges and selecting attendance statuses.

**Tech Stack:** Python 3.10+, XeLaTeX (`xcolor`, `tabularx`, `fontspec`), PyYAML, FastAPI, Uvicorn, Vanilla HTML5/CSS/JS.

---

## Global Constraints

- **Python Runtime:** Python 3.10+ (tested on Python 3.14).
- **LaTeX Engine:** XeLaTeX with `\usepackage{xcolor}` for colored status text.
- **Strict Layout Budget:** Exactly 1 week = 1 page A4 in all generated PDFs (signature block height strictly bounded ~3.2cm, row spacing calibrated so 5-day and 6-day weeks fit on single pages).
- **Attendance Formatting:** If status is `izin`, `sakit`, `cuti`, or `libur`: `jam_masuk` is `-`, `jam_pulang` is `-`, and activity text is rendered as `\textcolor{red}{\textbf{[{STATUS}]}: {Catatan Alasan}}`.
- **Signature Layout:** 2-tier layout (Student top right; "Mengetahui," center; Supervisor Lecturers bottom left & Field Mentor bottom right). Labels `NIM`, `NIP`, and `NIK` must be completely omitted.
- **Schedule Rules:** `senin_sabtu` includes Mon–Sat (Sat hours 08.00–14.00); `senin_jumat` excludes Saturday entirely (max 5 rows per table). Sunday is always off.
- **Backward Compatibility:** If `periode` is omitted in `config.yaml`, default to `2026-07-01` to `2026-12-31`. If notes in YAML are strings, default status to `hadir`.
- **Testing Standard:** 100% test pass rate across `python3 -m unittest discover tests`.

---

## File Structure

```text
log-book/
├── config.example.yaml                          # Updated: includes periode and hari_kerja schema
├── templates/
│   └── logbook_template.tex                     # Updated: includes \usepackage{xcolor}
├── scripts/
│   ├── calendar_utils.py                        # Updated: dynamic period range, 5/6 day logic, dynamic bundles
│   ├── data_manager.py                          # Updated: status object support & dynamic month templates
│   ├── latex_builder.py                         # Updated: red status text, 2-tier signature block without NIM/NIP/NIK
│   ├── narrative_expander.py                    # Unchanged (used for normal hadir notes)
│   └── doctor.py                                # Unchanged (xelatex pre-flight check)
├── main.py                                      # Updated: interactive setup wizard & dynamic month compilation
├── web/
│   ├── app.py                                   # Updated: dynamic calendar & status endpoints
│   └── static/
│       ├── index.html                           # Updated: attendance status dropdown & period date pickers
│       ├── styles.css                           # Updated: status badges and red text preview
│       └── app.js                               # Updated: reactive status selection, 5-day grid, period forms
└── tests/
    ├── test_latex_builder.py                    # Updated: tests for signature block & red status text
    ├── test_calendar_utils.py                   # Updated: tests for dynamic range & 5-day schedule
    ├── test_data_manager.py                     # Updated: tests for status objects & dynamic file loading
    ├── test_web_api.py                          # Updated: tests for /api/save-day status & dynamic calendar
    ├── test_web_static.py                       # Updated: tests for static HTML/CSS/JS status elements
    └── test_e2e.py                              # Updated: end-to-end verification with custom period & status
```

---

### Task 1: LaTeX Template & Redesigned 2-Tier Signature Block + Non-Hadir Red Text

**Files:**
- Modify: `templates/logbook_template.tex:1-10`
- Modify: `scripts/latex_builder.py:100-140`
- Test: `tests/test_latex_builder.py`

**Interfaces:**
- Consumes: `notes_map` (containing string or dict `{"status": "...", "kegiatan": "..."}`), `config`
- Produces: `render_week_page(...) -> str` with `\textcolor{red}{\textbf{[{STATUS}]:} ...}`, `-` work hours for non-hadir, and 2-tier signature block without `NIM`, `NIP`, `NIK`.

- [ ] **Step 1: Write the failing test in `tests/test_latex_builder.py`**

Add tests to `tests/test_latex_builder.py` asserting:
1. `\usepackage{xcolor}` is included in the compiled LaTeX document.
2. When a day has status `izin` or `sakit`, jam masuk/pulang are `-` and text contains `\textcolor{red}{\textbf{[IZIN]:} ...}`.
3. Signature block does NOT contain `NIM.`, `NIP.`, or `NIK.`.
4. Signature block has the 2-tier layout (`Mahasiswa` top right, `Mengetahui` center, `Dosen Pembimbing` bottom left, `Pembimbing Lapangan` bottom right).

```python
    def test_signature_block_two_tier_layout_without_id_labels(self):
        latex = generate_latex_document([self.weeks[0]], self.notes_map, self.config)
        # Verify no NIM, NIP, NIK in signature block
        self.assertNotIn("NIM.", latex)
        self.assertNotIn("NIP.", latex)
        self.assertNotIn("NIK.", latex)
        # Verify 2-tier structure
        self.assertIn("Mahasiswa,", latex)
        self.assertIn("Mengetahui,", latex)
        self.assertIn("Dosen Pembimbing,", latex)
        self.assertIn("Pembimbing Lapangan,", latex)

    def test_non_hadir_attendance_status_formatting(self):
        status_notes = {
            "2026-07-01": {"status": "izin", "kegiatan": "Izin menghadiri yudisium kampus"}
        }
        latex = generate_latex_document([self.weeks[0]], status_notes, self.config)
        # Hours should be '-'
        self.assertIn("& - & - &", latex)
        # Activity note should have red text and [IZIN]: label
        self.assertIn(r"\textcolor{red}{\textbf{[IZIN]:} Izin menghadiri yudisium kampus}", latex)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: FAIL with `AssertionError: 'NIM.' unexpectedly found in ...`.

- [ ] **Step 3: Update `templates/logbook_template.tex` and `scripts/latex_builder.py`**

In `templates/logbook_template.tex`, add `\usepackage{xcolor}` after line 3:
```latex
\documentclass[10pt,a4paper]{article}
\usepackage[a4paper, top=1.0cm, bottom=1.0cm, left=1.8cm, right=1.5cm, footskip=0.5cm]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\setmainfont{Liberation Serif}
```

In `scripts/latex_builder.py`, update row rendering and signature block:
```python
    # Rows for the table
    rows_tex = []
    for d in week_data["days"]:
        d_str = d["date_str"]
        hari_tgl = f"{d['hari']}, {d['tanggal_str']}"
        raw_val = notes_map.get(d_str, "")
        
        if isinstance(raw_val, dict):
            status = str(raw_val.get("status", "hadir")).strip().lower()
            activity_text = str(raw_val.get("kegiatan", "")).strip()
        else:
            status = "hadir"
            activity_text = str(raw_val).strip()

        if status in ("izin", "sakit", "cuti", "libur"):
            jam_masuk = "-"
            jam_pulang = "-"
            status_label = "LIBUR NASIONAL" if status == "libur" else status.upper()
            escaped_activity = escape_latex(activity_text)
            note_content = rf"\textcolor{{red}}{{\textbf{{[{status_label}]:}} {escaped_activity}}}"
        else:
            jam_masuk = d.get("jam_masuk", "08.00")
            jam_pulang = d.get("jam_pulang", "16.00")
            expanded = expand_narrative(activity_text)
            note_content = escape_latex(expanded)

        row = f"\\textbf{{{hari_tgl}}} & {jam_masuk} & {jam_pulang} & {note_content} \\\\"
        rows_tex.append(row)

    table_rows = "\n\\hline\n".join(rows_tex)

    table_tex = rf"""
\renewcommand{{\arraystretch}}{{1.15}}
\begin{{tabularx}}{{\textwidth}}{{|p{{3.8cm}}|c|c|X|}}
\hline
\textbf{{Hari, Tanggal}} & \textbf{{Jam Masuk}} & \textbf{{Jam Pulang}} & \textbf{{Kegiatan}} \\
\hline
{table_rows}
\hline
\end{{tabularx}}
\vspace{{0.2cm}}
"""

    # 2-Tier Signature Block (Without NIM, NIP, NIK labels)
    ttd_tex = rf"""
\hfill
\begin{{minipage}}{{0.40\textwidth}}
\centering
Mahasiswa,\\[1.3cm]
\textbf{{{nama_mhs}}}
\end{{minipage}}

\vspace{{0.15cm}}
\begin{{center}}
Mengetahui,
\end{{center}}
\vspace{{0.1cm}}

\noindent
\begin{{minipage}}[t]{{0.48\textwidth}}
\centering
Dosen Pembimbing,\\[1.3cm]
\textbf{{{nama_dosen}}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.48\textwidth}}
\centering
Pembimbing Lapangan,\\[1.3cm]
\textbf{{{nama_lapangan}}}
\end{{minipage}}
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_latex_builder.py`
Expected: PASS with all tests passing (including single-page 6-day week budget test).

- [ ] **Step 5: Commit changes**

```bash
git add templates/logbook_template.tex scripts/latex_builder.py tests/test_latex_builder.py
git commit -m "feat(latex): add xcolor, non-hadir red status text, and 2-tier signature block"
```

---

### Task 2: Dynamic Calendar Range, 5-Day/6-Day Schedule & Monthly Bundler

**Files:**
- Modify: `scripts/calendar_utils.py`
- Modify: `tests/test_calendar_utils.py`

**Interfaces:**
- Consumes: `config: dict | None`
- Produces: 
  - `get_internship_calendar(config: dict | None = None, start_date: datetime.date | None = None, end_date: datetime.date | None = None, work_days: str | None = None) -> list[dict]`
  - `get_month_bundles(config: dict | None = None) -> list[dict]`
  - `get_month_bundle_weeks(bundle_index: int, config: dict | None = None) -> list[dict]`
  - `get_yaml_filename_for_date(d: datetime.date, config: dict | None = None) -> str`

- [ ] **Step 1: Write the failing tests in `tests/test_calendar_utils.py`**

```python
    def test_dynamic_calendar_custom_range_and_five_day_schedule(self):
        cfg = {
            "periode": {
                "tanggal_mulai": "2026-08-03",
                "tanggal_selesai": "2026-09-11"
            },
            "pengaturan": {
                "hari_kerja": "senin_jumat"
            }
        }
        weeks = get_internship_calendar(cfg)
        self.assertTrue(len(weeks) > 0)
        # Verify no Saturday in any week
        for w in weeks:
            for d in w["days"]:
                self.assertNotEqual(d["hari"], "Sabtu")
                self.assertNotEqual(d["hari"], "Minggu")
                self.assertIn(d["jam_pulang"], ["16.00"])

    def test_dynamic_month_bundles(self):
        cfg = {
            "periode": {
                "tanggal_mulai": "2026-08-01",
                "tanggal_selesai": "2026-10-31"
            },
            "pengaturan": {
                "hari_kerja": "senin_sabtu"
            }
        }
        bundles = get_month_bundles(cfg)
        self.assertEqual(len(bundles), 3) # Agustus, September, Oktober
        self.assertEqual(bundles[0]["month_name"], "Agustus")
        self.assertEqual(bundles[1]["month_name"], "September")
        self.assertEqual(bundles[2]["month_name"], "Oktober")
        self.assertEqual(bundles[0]["filename"], "Logbook_01_Agustus_2026.pdf")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: FAIL with `NameError: name 'get_month_bundles' is not defined` or `TypeError`.

- [ ] **Step 3: Implement dynamic calendar logic in `scripts/calendar_utils.py`**

Refactor `scripts/calendar_utils.py`:
1. Expand `INDONESIAN_MONTHS` to all 12 months (1..12).
2. Update `get_internship_calendar` to parse `config.get("periode", {})` and `config.get("pengaturan", {}).get("hari_kerja", "senin_sabtu")`.
3. Support `senin_jumat` (Monday–Friday, skipping Saturday and Sunday, ending week on Friday or final day).
4. Implement `get_month_bundles(config=None) -> list[dict]` grouping weeks by their dominant calendar month.
5. Update `get_month_bundle_weeks(bundle_index, config=None)` to look up weeks from `get_month_bundles`.
6. Update `get_yaml_filename_for_date(d, config=None)` to map to `bulan_{index:02d}_{month_name.lower()}.yaml`.

```python
# scripts/calendar_utils.py
import datetime
from typing import Optional, List, Dict, Tuple

INDONESIAN_DAYS: dict[int, str] = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

INDONESIAN_MONTHS: dict[int, str] = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

DEFAULT_START_DATE = datetime.date(2026, 7, 1)
DEFAULT_END_DATE = datetime.date(2026, 12, 31)

def format_indonesian_date(d: datetime.date) -> str:
    month_name = INDONESIAN_MONTHS.get(d.month, str(d.month))
    return f"{d.day} {month_name} {d.year}"

def parse_config_period(config: Optional[dict] = None) -> Tuple[datetime.date, datetime.date, str]:
    if not config:
        return DEFAULT_START_DATE, DEFAULT_END_DATE, "senin_sabtu"
    
    periode = config.get("periode", {})
    start_str = periode.get("tanggal_mulai")
    end_str = periode.get("tanggal_selesai")
    
    start_d = datetime.date.fromisoformat(str(start_str)) if start_str else DEFAULT_START_DATE
    end_d = datetime.date.fromisoformat(str(end_str)) if end_str else DEFAULT_END_DATE
    
    hari_kerja = config.get("pengaturan", {}).get("hari_kerja", "senin_sabtu")
    if hari_kerja not in ("senin_jumat", "senin_sabtu"):
        hari_kerja = "senin_sabtu"
        
    return start_d, end_d, hari_kerja

def get_internship_calendar(
    config: Optional[dict] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    work_days: Optional[str] = None
) -> List[dict]:
    cfg_start, cfg_end, cfg_work = parse_config_period(config)
    start_d = start_date or cfg_start
    end_d = end_date or cfg_end
    work_days_mode = work_days or cfg_work

    weeks = []
    current_days = []
    curr = start_d
    week_num = 1

    jam_senin_jumat_masuk = "08.00"
    jam_senin_jumat_pulang = "16.00"
    jam_sabtu_pulang = "14.00"
    if config and "pengaturan" in config:
        jam_cfg = config["pengaturan"].get("jam_kerja", {})
        jam_senin_jumat_masuk = jam_cfg.get("senin_jumat", {}).get("masuk", "08.00")
        jam_senin_jumat_pulang = jam_cfg.get("senin_jumat", {}).get("pulang", "16.00")
        jam_sabtu_pulang = jam_cfg.get("sabtu", {}).get("pulang", "14.00")

    while curr <= end_d:
        w_day = curr.weekday()
        is_active = False

        if work_days_mode == "senin_jumat" and w_day in range(0, 5): # Mon-Fri
            is_active = True
            jam_masuk = jam_senin_jumat_masuk
            jam_pulang = jam_senin_jumat_pulang
        elif work_days_mode == "senin_sabtu" and w_day in range(0, 6): # Mon-Sat
            is_active = True
            jam_masuk = jam_senin_jumat_masuk
            jam_pulang = jam_sabtu_pulang if w_day == 5 else jam_senin_jumat_pulang

        if is_active:
            current_days.append({
                "date": curr,
                "date_str": curr.strftime("%Y-%m-%d"),
                "hari": INDONESIAN_DAYS[w_day],
                "tanggal_str": format_indonesian_date(curr),
                "jam_masuk": jam_masuk,
                "jam_pulang": jam_pulang,
            })

        end_of_week = (work_days_mode == "senin_jumat" and w_day == 4) or \
                      (work_days_mode == "senin_sabtu" and w_day == 5) or \
                      (curr == end_d)

        if end_of_week:
            if current_days:
                weeks.append({
                    "minggu_ke": week_num,
                    "days": current_days
                })
                week_num += 1
                current_days = []

        curr += datetime.timedelta(days=1)

    return weeks

def get_month_bundles(config: Optional[dict] = None) -> List[dict]:
    all_weeks = get_internship_calendar(config)
    if not all_weeks:
        return []

    # Identify dominant (year, month) for each week
    from collections import Counter
    month_week_map = {} # (year, month) -> list of weeks
    for w in all_weeks:
        months_in_week = [d["date"].month for d in w["days"]]
        years_in_week = [d["date"].year for d in w["days"]]
        dominant_month = Counter(months_in_week).most_common(1)[0][0]
        # find corresponding year
        for d in w["days"]:
            if d["date"].month == dominant_month:
                dominant_year = d["date"].year
                break
        key = (dominant_year, dominant_month)
        month_week_map.setdefault(key, []).append(w)

    bundles = []
    bundle_idx = 1
    # Sort keys chronologically
    sorted_keys = sorted(month_week_map.keys())
    for yr, mo in sorted_keys:
        weeks_in_bundle = month_week_map[(yr, mo)]
        month_name = INDONESIAN_MONTHS.get(mo, str(mo))
        w_start = weeks_in_bundle[0]["minggu_ke"]
        w_end = weeks_in_bundle[-1]["minggu_ke"]
        bundles.append({
            "bundle_index": bundle_idx,
            "month": mo,
            "year": yr,
            "month_name": month_name,
            "name": f"{month_name} {yr}",
            "filename": f"Logbook_{bundle_idx:02d}_{month_name}_{yr}.pdf",
            "yaml_filename": f"bulan_{bundle_idx:02d}_{month_name.lower()}.yaml",
            "start_week": w_start,
            "end_week": w_end,
            "weeks": weeks_in_bundle
        })
        bundle_idx += 1

    return bundles

def get_month_bundle_weeks(bundle_index: int, config: Optional[dict] = None) -> List[dict]:
    bundles = get_month_bundles(config)
    for b in bundles:
        if b["bundle_index"] == bundle_index:
            return b["weeks"]
    raise ValueError(f"Bundle index {bundle_index} tidak ditemukan dalam periode kalender.")

def get_yaml_filename_for_date(d: datetime.date, config: Optional[dict] = None) -> str:
    bundles = get_month_bundles(config)
    for b in bundles:
        for w in b["weeks"]:
            for day in w["days"]:
                if day["date"] == d:
                    return b["yaml_filename"]
    # Fallback by calendar month
    mo_name = INDONESIAN_MONTHS.get(d.month, "bulan").lower()
    return f"bulan_{d.month:02d}_{mo_name}.yaml"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: PASS with 100% tests passing.

- [ ] **Step 5: Commit changes**

```bash
git add scripts/calendar_utils.py tests/test_calendar_utils.py
git commit -m "feat(calendar): support dynamic period dates, 5-day schedule, and automatic month bundling"
```

---

### Task 3: Data Manager Support for Dynamic Months & Attendance Status

**Files:**
- Modify: `scripts/data_manager.py`
- Modify: `tests/test_data_manager.py`

**Interfaces:**
- Consumes: `scripts.calendar_utils.get_month_bundles`, `config: dict | None`
- Produces: 
  - `init_data_files(data_dir: str = "data", config: dict | None = None) -> None`
  - `load_all_notes(data_dir: str = "data", config: dict | None = None) -> dict[str, Any]`
  - `save_note_to_month(date_val: datetime.date, note: str | dict, data_dir: str = "data", config: dict | None = None) -> None`

- [ ] **Step 1: Write the failing tests in `tests/test_data_manager.py`**

```python
    def test_save_and_load_attendance_status_object(self):
        tmp_dir = tempfile.mkdtemp(prefix="test_data_status_")
        try:
            d = datetime.date(2026, 7, 10)
            status_payload = {
                "status": "izin",
                "kegiatan": "Izin menghadiri pernikahan keluarga"
            }
            save_note_to_month(d, status_payload, data_dir=tmp_dir)
            
            notes = load_all_notes(data_dir=tmp_dir)
            self.assertIn("2026-07-10", notes)
            self.assertIsInstance(notes["2026-07-10"], dict)
            self.assertEqual(notes["2026-07-10"]["status"], "izin")
            self.assertEqual(notes["2026-07-10"]["kegiatan"], "Izin menghadiri pernikahan keluarga")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_data_manager.py`
Expected: FAIL because `load_all_notes` previously converted everything to string (`str(v).strip()`).

- [ ] **Step 3: Update `scripts/data_manager.py`**

Update `init_data_files`, `load_all_notes`, and `save_note_to_month`:
```python
def get_month_templates(config: Optional[dict] = None) -> List[Tuple[int, int, str]]:
    bundles = get_month_bundles(config)
    if bundles:
        return [(b["month"], b["year"], b["yaml_filename"]) for b in bundles]
    return [
        (7, 2026, "bulan_01_juli.yaml"),
        (8, 2026, "bulan_02_agustus.yaml"),
        (9, 2026, "bulan_03_september.yaml"),
        (10, 2026, "bulan_04_oktober.yaml"),
        (11, 2026, "bulan_05_november.yaml"),
        (12, 2026, "bulan_06_desember.yaml"),
    ]

def init_data_files(data_dir: str = "data", config: Optional[dict] = None) -> None:
    target_path = Path(data_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    templates = get_month_templates(config)

    for bulan, tahun, filename in templates:
        file_path = target_path / filename
        if not file_path.exists():
            content = {
                "bulan": bulan,
                "tahun": tahun,
                "catatan": {}
            }
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, allow_unicode=True, default_flow_style=False)

def load_all_notes(data_dir: str = "data", config: Optional[dict] = None) -> dict:
    init_data_files(data_dir, config)
    target_path = Path(data_dir)
    merged_notes = {}
    templates = get_month_templates(config)

    for _, _, filename in templates:
        file_path = target_path / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                catatan = data.get("catatan") or {}
                for k, v in catatan.items():
                    if v is not None:
                        k_str = k.strftime("%Y-%m-%d") if isinstance(k, (datetime.date, datetime.datetime)) else str(k)
                        if isinstance(v, dict):
                            merged_notes[k_str] = {
                                "status": str(v.get("status", "hadir")).strip().lower(),
                                "kegiatan": str(v.get("kegiatan", "")).strip()
                            }
                        elif str(v).strip():
                            merged_notes[k_str] = str(v).strip()

    return merged_notes

def save_note_to_month(date_val: datetime.date, note: Any, data_dir: str = "data", config: Optional[dict] = None) -> None:
    filename = get_yaml_filename_for_date(date_val, config)
    target_path = Path(data_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    file_path = target_path / filename

    data = {}
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    if "bulan" not in data:
        data["bulan"] = date_val.month
    if "tahun" not in data:
        data["tahun"] = date_val.year
    if "catatan" not in data or not isinstance(data["catatan"], dict):
        data["catatan"] = {}

    date_str = date_val.strftime("%Y-%m-%d")
    data["catatan"][date_str] = note

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_data_manager.py`
Expected: PASS with 100% tests passing.

- [ ] **Step 5: Commit changes**

```bash
git add scripts/data_manager.py tests/test_data_manager.py
git commit -m "feat(data): support structured attendance status and dynamic month file templates"
```

---

### Task 4: CLI Setup Wizard, Dynamic Build Orchestration & Config

**Files:**
- Modify: `config.example.yaml`
- Modify: `main.py`
- Modify: `tests/test_main.py`

**Interfaces:**
- Consumes: `scripts.calendar_utils.get_month_bundles`, `scripts.calendar_utils.get_internship_calendar`
- Produces: 
  - `run_setup_wizard(config_path: str = "config.yaml") -> dict`
  - Dynamic build pipeline in `main.py` generating PDFs based on active month bundles.

- [ ] **Step 1: Write tests in `tests/test_main.py` for wizard & dynamic build**

```python
    @patch("builtins.input")
    def test_run_setup_wizard(self, mock_input):
        # Provide inputs: Nama, NIM, Prodi, Mitra, Tgl Mulai, Tgl Selesai, Jadwal, Dosen, NIP, Mentor, NIK
        mock_input.side_effect = [
            "Ahmad Fauzi",
            "2241720005",
            "Sarjana Terapan Teknik Informatika",
            "PT Digital Inovasi",
            "2026-08-01",
            "2026-11-30",
            "1", # 5 hari
            "Dr. Dosen, M.Kom.",
            "19850101",
            "Budi Santoso",
            "EMP-01"
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_config.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["mahasiswa"]["nama"], "Ahmad Fauzi")
            self.assertEqual(cfg["periode"]["tanggal_mulai"], "2026-08-01")
            self.assertEqual(cfg["pengaturan"]["hari_kerja"], "senin_jumat")
            self.assertTrue(os.path.exists(cfg_path))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_main.py`
Expected: FAIL with `NameError: name 'run_setup_wizard' is not defined`.

- [ ] **Step 3: Update `config.example.yaml` and `main.py`**

In `config.example.yaml`, add `periode` and `hari_kerja`:
```yaml
mahasiswa:
  nama: "Nama Lengkap Mahasiswa"
  nim: "XXXXXXXXXX"
  prodi: "Sarjana Terapan Teknik Informatika"
  mitra: "Nama Perusahaan / Tempat Magang"

periode:
  tanggal_mulai: "2026-07-01"
  tanggal_selesai: "2026-12-31"

pengaturan:
  hari_kerja: "senin_sabtu" # Pilihan: "senin_jumat" (5 hari) atau "senin_sabtu" (6 hari)
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

In `main.py`:
1. Implement `run_setup_wizard(config_path="config.yaml") -> dict`.
2. Add `--init` argument to run setup wizard explicitly.
3. Update `build_pdf_bundle` and main loop to retrieve bundles via `get_month_bundles(config)` instead of static 6-month dictionary.

```python
def run_setup_wizard(config_path: str = "config.yaml") -> dict:
    print("\n========================================================")
    print("🪄 WIZARD KONFIGURASI LOG BOOK MAGANG POLINEMA")
    print("========================================================\n")
    
    nama = input("Nama Mahasiswa: ").strip() or "Nama Mahasiswa"
    nim = input("NIM: ").strip() or "XXXXXXXXXX"
    prodi = input("Program Studi [Sarjana Terapan Teknik Informatika]: ").strip() or "Sarjana Terapan Teknik Informatika"
    mitra = input("Nama Mitra Industri: ").strip() or "Mitra Industri"
    
    tgl_mulai = input("Tanggal Mulai Magang (YYYY-MM-DD) [2026-07-01]: ").strip() or "2026-07-01"
    tgl_selesai = input("Tanggal Selesai Magang (YYYY-MM-DD) [2026-12-31]: ").strip() or "2026-12-31"
    
    print("\nPilih Jadwal Kerja:")
    print("  1. 5 Hari Kerja (Senin - Jumat)")
    print("  2. 6 Hari Kerja (Senin - Sabtu)")
    jadwal_opt = input("Pilihan [2]: ").strip() or "2"
    hari_kerja = "senin_jumat" if jadwal_opt == "1" else "senin_sabtu"

    nama_dosen = input("\nNama Dosen Pembimbing: ").strip() or ""
    nip_dosen = input("NIP Dosen Pembimbing: ").strip() or ""
    nama_lapangan = input("Nama Pembimbing Lapangan (Mentor): ").strip() or ""
    nik_lapangan = input("NIK / ID Pembimbing Lapangan: ").strip() or ""

    config = {
        "mahasiswa": {"nama": nama, "nim": nim, "prodi": prodi, "mitra": mitra},
        "periode": {"tanggal_mulai": tgl_mulai, "tanggal_selesai": tgl_selesai},
        "pengaturan": {
            "hari_kerja": hari_kerja,
            "jam_kerja": {
                "senin_jumat": {"masuk": "08.00", "pulang": "16.00"},
                "sabtu": {"masuk": "08.00", "pulang": "14.00"}
            }
        },
        "pembimbing": {
            "dosen": {"nama": nama_dosen, "nip": nip_dosen},
            "lapangan": {"nama": nama_lapangan, "nik": nik_lapangan}
        }
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n[OK] Konfigurasi berhasil disimpan ke '{config_path}'.\n")
    return config
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_main.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add config.example.yaml main.py tests/test_main.py
git commit -m "feat(cli): add interactive setup wizard and dynamic month build pipeline"
```

---

### Task 5: FastAPI Backend Endpoints & Calendar/Status API

**Files:**
- Modify: `web/app.py`
- Modify: `tests/test_web_api.py`

**Interfaces:**
- Consumes: `scripts.calendar_utils.get_month_bundles`, `scripts.calendar_utils.get_internship_calendar`, `scripts.data_manager.save_note_to_month`
- Produces: 
  - `POST /api/save-day` accepting `status` and `note`.
  - `GET /api/calendar` returning dynamic bundles and working days based on `config.yaml`.
  - `POST /api/generate-pdf` building dynamic monthly PDFs.

- [ ] **Step 1: Write failing tests in `tests/test_web_api.py`**

```python
    def test_save_day_with_attendance_status(self):
        payload = {
            "date": "2026-07-02",
            "status": "sakit",
            "note": "Surat dokter terlampir"
        }
        res = self.client.post("/api/save-day", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["attendance_status"], "sakit")

    def test_calendar_reflects_five_day_setting(self):
        # Update config to 5-day
        cfg_res = self.client.get("/api/config")
        cfg = cfg_res.json()
        cfg["pengaturan"]["hari_kerja"] = "senin_jumat"
        self.client.post("/api/config", json=cfg)

        cal_res = self.client.get("/api/calendar")
        self.assertEqual(cal_res.status_code, 200)
        cal_data = cal_res.json()
        # Ensure no Saturday in returned calendar days
        for m in cal_data["months"]:
            for w in m["weeks"]:
                for d in w["days"]:
                    self.assertNotEqual(d["hari"], "Sabtu")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: FAIL because `SaveDayRequest` did not return `attendance_status` and calendar did not reload dynamic `hari_kerja`.

- [ ] **Step 3: Update `web/app.py`**

1. Update `SaveDayRequest`:
```python
class SaveDayRequest(BaseModel):
    date: str
    note: str
    status: str = "hadir"
```
2. In `save_day(payload)`:
If `payload.status != "hadir"`:
Save `{"status": payload.status, "kegiatan": payload.note}`.
Otherwise save `payload.note`.
Return `{"status": "ok", "date": payload.date, "note": payload.note, "attendance_status": payload.status}`.
3. In `get_calendar()`:
Call `config = load_config("config.yaml")`, `get_internship_calendar(config)`, and build `months_data` from `get_month_bundles(config)`.
Include `attendance_status` and `kegiatan` for each day info.
4. In `generate_pdf()`:
Dynamically handle targets using `get_month_bundles(config)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add web/app.py tests/test_web_api.py
git commit -m "feat(api): support attendance status and dynamic period calendar in REST API"
```

---

### Task 6: Frontend Bento Grid UI, Attendance Modal & Config Wizard

**Files:**
- Modify: `web/static/index.html`
- Modify: `web/static/styles.css`
- Modify: `web/static/app.js`
- Test: `tests/test_web_static.py`

**Interfaces:**
- Consumes: `/api/calendar`, `/api/save-day`, `/api/config`
- Produces: Interactive SPA with status selector, non-hadir styling, and configuration date pickers.

- [ ] **Step 1: Write test assertions in `tests/test_web_static.py`**

Assert that:
1. `index.html` contains `#editor-status`, `#cfg-periode-mulai`, `#cfg-periode-selesai`, and `cfg-hari-kerja`.
2. `styles.css` contains `.badge-izin`, `.badge-sakit`, `.badge-cuti`, `.badge-libur`, and `.text-danger`.
3. `app.js` handles `editor-status` change and renders attendance status badges.

```python
    def test_attendance_and_period_elements_present_in_static_files(self):
        res_html = self.client.get("/")
        self.assertIn('id="editor-status"', res_html.text)
        self.assertIn('id="cfg-periode-mulai"', res_html.text)
        self.assertIn('id="cfg-periode-selesai"', res_html.text)
        self.assertIn('name="cfg-hari-kerja"', res_html.text)

        res_css = self.client.get("/static/styles.css")
        self.assertIn('.badge-izin', res_css.text)
        self.assertIn('.text-danger', res_css.text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: FAIL with `AssertionError: 'id="editor-status"' not found in ...`.

- [ ] **Step 3: Update `web/static/index.html`, `styles.css`, and `app.js`**

1. In `web/static/index.html`:
Add Attendance Status select to `#modal-editor`:
```html
<div class="form-group">
  <label for="editor-status" class="form-label">Status Kehadiran</label>
  <select id="editor-status" class="form-select">
    <option value="hadir">Hadir (Bekerja Normal)</option>
    <option value="izin">Izin</option>
    <option value="sakit">Sakit</option>
    <option value="cuti">Cuti</option>
    <option value="libur">Libur Nasional</option>
  </select>
</div>
```
Add Period & Workdays inputs to `#modal-config`:
```html
<h4 class="section-title">Periode & Jadwal Magang</h4>
<div class="form-row">
  <div class="form-col">
    <label for="cfg-periode-mulai" class="form-label">Tanggal Mulai Magang</label>
    <input type="date" id="cfg-periode-mulai" class="form-input" required>
  </div>
  <div class="form-col">
    <label for="cfg-periode-selesai" class="form-label">Tanggal Selesai Magang</label>
    <input type="date" id="cfg-periode-selesai" class="form-input" required>
  </div>
</div>
<div class="form-group">
  <label class="form-label">Jadwal Hari Kerja</label>
  <div class="radio-group">
    <label class="radio-label">
      <input type="radio" name="cfg-hari-kerja" value="senin_sabtu" checked>
      <span>6 Hari Kerja (Senin - Sabtu)</span>
    </label>
    <label class="radio-label">
      <input type="radio" name="cfg-hari-kerja" value="senin_jumat">
      <span>5 Hari Kerja (Senin - Jumat)</span>
    </label>
  </div>
</div>
```

2. In `web/static/styles.css`:
Add styles for badges and danger text:
```css
.badge-izin { background-color: #FEF3C7; color: #B45309; }
.badge-sakit { background-color: #FEE2E2; color: #B91C1C; }
.badge-cuti { background-color: #E0E7FF; color: #4338CA; }
.badge-libur { background-color: #F3F4F6; color: #4B5563; }
.text-danger { color: #EF4444 !important; font-weight: 600; }
[data-theme="dark"] .badge-izin { background-color: rgba(245, 158, 11, 0.2); color: #FCD34D; }
[data-theme="dark"] .badge-sakit { background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5; }
[data-theme="dark"] .badge-cuti { background-color: rgba(99, 102, 241, 0.2); color: #A5B4FC; }
[data-theme="dark"] .badge-libur { background-color: rgba(156, 163, 175, 0.2); color: #D1D5DB; }
```

3. In `web/static/app.js`:
- On `openEditModal`: set `#editor-status` value from day object (`d.status || 'hadir'`).
- Add event listener on `#editor-status` to disable work hours inputs and toggle button visibility if non-hadir.
- On save: send `{date, note, status}`.
- In `renderApp`: render badge with appropriate status label and color class.
- In `openConfigModal` and `saveConfig`: populate and save `periode.tanggal_mulai`, `periode.tanggal_selesai`, and `pengaturan.hari_kerja`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add web/static/index.html web/static/styles.css web/static/app.js tests/test_web_static.py
git commit -m "feat(ui): add attendance status selector, 5-day layout, and period settings in dashboard"
```

---

### Task 7: Full E2E Dynamic Build & Verification

**Files:**
- Modify: `tests/test_e2e.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: All components from Tasks 1–6
- Produces: Passing E2E test suite verifying custom period, non-hadir status red text compilation, 2-tier signatures, and updated documentation.

- [ ] **Step 1: Update `tests/test_e2e.py` to verify non-hadir status and signatures**

```python
    def test_build_with_status_and_new_signature(self):
        # Build month 1
        res = subprocess.run(
            [sys.executable, "main.py", "--month", "1", "--non-interactive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"Build failed: {res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext not found")

        pdftotext_res = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, text=True)
        out_text = pdftotext_res.stdout.lower()

        # Invariant checks
        self.assertIn("log book kegiatan", out_text)
        self.assertIn("mengetahui", out_text)
        self.assertIn("dosen pembimbing", out_text)
        self.assertIn("pembimbing lapangan", out_text)
        # Ensure NIM., NIP., NIK. are not in the signature block
        self.assertNotIn("nim.", out_text)
        self.assertNotIn("nip.", out_text)
        self.assertNotIn("nik.", out_text)
```

- [ ] **Step 2: Run E2E test**

Run: `python3 -m unittest tests/test_e2e.py`
Expected: PASS.

- [ ] **Step 3: Update `README.md` documentation**

Document:
1. Dynamic period configuration (`periode.tanggal_mulai` and `tanggal_selesai`).
2. 5-Day vs 6-Day work schedule (`pengaturan.hari_kerja`).
3. Attendance status options (`Hadir`, `Izin`, `Sakit`, `Cuti`, `Libur Nasional`) with automatic red text formatting.
4. Redesigned 2-tier signature layout.
5. CLI setup wizard command (`python3 main.py --init`).

- [ ] **Step 4: Run full test suite to verify 100% pass**

Run: `python3 -m unittest discover tests`
Expected: PASS with 100% of tests passing (0 failures, 0 errors).

- [ ] **Step 5: Commit changes**

```bash
git add tests/test_e2e.py README.md
git commit -m "docs: document dynamic period, attendance status, and 2-tier signature redesign"
```

---

## Plan Self-Review Checklist

- **Spec Coverage:**
  - Dynamic Period (start date, end date): Covered in Tasks 2, 4, 5, 6.
  - Flexible Work Days (5-day vs 6-day): Covered in Tasks 2, 4, 5, 6.
  - Attendance Status (`hadir`, `izin`, `sakit`, `cuti`, `libur`) with red text and `-` hours: Covered in Tasks 1, 3, 5, 6.
  - 2-Tier Signature Block without NIM/NIP/NIK: Covered in Tasks 1, 7.
  - Setup Wizard (CLI and Web UI): Covered in Tasks 4, 6.
- **Placeholder Scan:** No "TODO", "TBD", or unwritten steps. Every step contains complete code, exact commands, and expected outputs.
- **Type Consistency:** Function names (`get_internship_calendar`, `get_month_bundles`, `run_setup_wizard`, `save_note_to_month`) match across implementations and tests.
