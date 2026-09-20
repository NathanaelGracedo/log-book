# Per-Day Working Hours & Streamlined Supervisor Form Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement granular per-day working hours configuration (`pengaturan.jam_kerja` for Senin through Sabtu), auto-populate daily work hours on `Hadir` status, streamline the supervisor configuration by completely removing NIP and NIK fields from forms and wizards, and ensure dynamic 5-day / 6-day UI toggling.

**Architecture:** Extend `scripts/calendar_utils.py` to resolve work hours per day of the week from `config["pengaturan"]["jam_kerja"]` with backwards-compatible fallback. Update `main.py` CLI setup wizard to remove NIP/NIK prompts and support per-day working hours with quick defaults. Update `web/app.py` and Bento Grid SPA (`web/static/index.html`, `styles.css`, `app.js`) to provide an interactive per-day hours table in the settings modal with dynamic Saturday row toggling, auto-fill hours on `Hadir`, and eliminate all NIP/NIK inputs.

**Tech Stack:** Python 3.10+, XeLaTeX, PyYAML, FastAPI, Uvicorn, Vanilla HTML5/CSS3/ES6+ JavaScript.

---

## Global Constraints

- **Python Runtime:** Python 3.10+ (tested on Python 3.14).
- **LaTeX Engine:** XeLaTeX with `\usepackage{xcolor}` and 1 week = 1 page A4 layout constraint.
- **Per-Day Working Hours Schema:** `pengaturan.jam_kerja` dictionary mapping `senin`, `selasa`, `rabu`, `kamis`, `jumat`, and `sabtu` to `{ masuk: "HH.MM", pulang: "HH.MM" }`.
- **Backwards Compatibility:** Legacy config with `senin_jumat` and `sabtu` must continue to work without breaking.
- **Supervisor Privacy & Simplicity:** No NIP or NIK fields in user-facing wizards or Web UI settings forms; `config["pembimbing"]` stores only `{ dosen: { nama: ... }, lapangan: { nama: ... } }`.
- **Zero NPM/Node Dependencies:** Frontend remains vanilla HTML5, CSS3, and ES6+ JavaScript.
- **Testing Standard:** 100% test pass rate across `python3 -m unittest discover tests`.

---

## File Structure

```text
log-book/
├── config.example.yaml                          # Updated: per-day jam_kerja schema and removed nip/nik keys
├── scripts/
│   └── calendar_utils.py                        # Updated: per-day working hours resolution & fallback
├── main.py                                      # Updated: wizard removes NIP/NIK, prompts for per-day hours
├── web/
│   ├── app.py                                   # Verified: calendar enrichment preserves per-day hours
│   └── static/
│       ├── index.html                           # Updated: per-day hours table, removed NIP/NIK fields
│       ├── styles.css                           # Updated: hours table styling and dynamic row toggle
│       └── app.js                               # Updated: load/save per-day hours, toggle Saturday row, hadir auto-hours
└── tests/
    ├── test_calendar_utils.py                   # Updated: unit tests for per-day working hours resolution
    ├── test_main.py                             # Updated: tests for streamlined wizard & per-day hours
    ├── test_web_api.py                          # Updated: tests for per-day hours & streamlined supervisor config
    ├── test_web_static.py                       # Updated: tests asserting no NIP/NIK inputs and hours table exists
    └── test_e2e.py                              # Updated: E2E build test with custom per-day hours
```

---

### Task 1: Per-Day Working Hours Schema & Calendar Integration

**Files:**
- Modify: `config.example.yaml:18-35`
- Modify: `scripts/calendar_utils.py:89-122`
- Test: `tests/test_calendar_utils.py`

**Interfaces:**
- Consumes: `config.get("pengaturan", {}).get("jam_kerja")` containing per-day keys (`senin`, `selasa`, `rabu`, `kamis`, `jumat`, `sabtu`) or legacy keys (`senin_jumat`, `sabtu`).
- Produces: `get_internship_calendar(config=None)` returns day items where `jam_masuk` and `jam_pulang` match each day's configured schedule.

- [ ] **Step 1: Write failing tests in `tests/test_calendar_utils.py`**

Add tests verifying:
1. When custom per-day hours are specified (e.g. Jumat pulang 11.30, Rabu masuk 07.30), those exact hours appear on Wednesday and Friday in `get_internship_calendar(config)`.
2. Backwards compatibility works when legacy `senin_jumat` and `sabtu` keys are present.
3. Safe defaults are used when `jam_kerja` is missing or empty.

```python
    def test_per_day_working_hours_resolution(self):
        custom_config = {
            "periode": {"tanggal_mulai": "2026-07-01", "tanggal_selesai": "2026-07-04"}, # Wed to Sat
            "pengaturan": {
                "hari_kerja": "senin_sabtu",
                "jam_kerja": {
                    "senin": {"masuk": "08.00", "pulang": "16.00"},
                    "selasa": {"masuk": "08.00", "pulang": "16.00"},
                    "rabu": {"masuk": "07.30", "pulang": "15.30"},
                    "kamis": {"masuk": "08.00", "pulang": "16.00"},
                    "jumat": {"masuk": "08.00", "pulang": "11.30"},
                    "sabtu": {"masuk": "08.30", "pulang": "13.00"},
                }
            }
        }
        weeks = get_internship_calendar(config=custom_config)
        self.assertEqual(len(weeks), 1)
        days = weeks[0]["days"]
        # Wednesday (Rabu - 2026-07-01)
        self.assertEqual(days[0]["hari"], "Rabu")
        self.assertEqual(days[0]["jam_masuk"], "07.30")
        self.assertEqual(days[0]["jam_pulang"], "15.30")
        # Thursday (Kamis - 2026-07-02)
        self.assertEqual(days[1]["hari"], "Kamis")
        self.assertEqual(days[1]["jam_masuk"], "08.00")
        self.assertEqual(days[1]["jam_pulang"], "16.00")
        # Friday (Jumat - 2026-07-03)
        self.assertEqual(days[2]["hari"], "Jumat")
        self.assertEqual(days[2]["jam_masuk"], "08.00")
        self.assertEqual(days[2]["jam_pulang"], "11.30")
        # Saturday (Sabtu - 2026-07-04)
        self.assertEqual(days[3]["hari"], "Sabtu")
        self.assertEqual(days[3]["jam_masuk"], "08.30")
        self.assertEqual(days[3]["jam_pulang"], "13.00")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: FAIL because `calendar_utils.py` currently only reads `senin_jumat` and ignores `rabu`, `jumat`, etc.

- [ ] **Step 3: Implement minimal code in `scripts/calendar_utils.py` and `config.example.yaml`**

In `scripts/calendar_utils.py`:
Add day mapping constant:
```python
DAY_KEYS = {
    0: "senin",
    1: "selasa",
    2: "rabu",
    3: "kamis",
    4: "jumat",
    5: "sabtu"
}
```

In `get_internship_calendar(...)`:
```python
    jam_cfg = (config.get("pengaturan") or {}).get("jam_kerja") or {} if config else {}
    # Legacy fallbacks
    legacy_sj = jam_cfg.get("senin_jumat") or {}
    legacy_sabtu = jam_cfg.get("sabtu") or {}
```

Inside the loop when `is_active` is True:
```python
        day_key = DAY_KEYS.get(w_day)
        day_spec = jam_cfg.get(day_key) if isinstance(jam_cfg.get(day_key), dict) else None

        if day_spec:
            jam_masuk = day_spec.get("masuk") or "08.00"
            jam_pulang = day_spec.get("pulang") or ("14.00" if w_day == 5 else "16.00")
        else:
            # Fallback to legacy structure or defaults
            if w_day == 5:
                jam_masuk = legacy_sabtu.get("masuk") or "08.00"
                jam_pulang = legacy_sabtu.get("pulang") or "14.00"
            else:
                jam_masuk = legacy_sj.get("masuk") or "08.00"
                jam_pulang = legacy_sj.get("pulang") or "16.00"
```

In `config.example.yaml`:
Update `pengaturan.jam_kerja` to per-day format, and remove `nip` and `nik` under `pembimbing`:
```yaml
pengaturan:
  hari_kerja: "senin_sabtu" # Pilihan: "senin_jumat" (5 hari) atau "senin_sabtu" (6 hari)
  jam_kerja:
    senin:  { masuk: "08.00", pulang: "16.00" }
    selasa: { masuk: "08.00", pulang: "16.00" }
    rabu:   { masuk: "08.00", pulang: "16.00" }
    kamis:  { masuk: "08.00", pulang: "16.00" }
    jumat:  { masuk: "08.00", pulang: "16.00" }
    sabtu:  { masuk: "08.00", pulang: "14.00" }

pembimbing:
  dosen:
    nama: "Nama Dosen Pembimbing, S.Kom., M.Kom."
  lapangan:
    nama: "Nama Pembimbing Lapangan / Mentor"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests/test_calendar_utils.py`
Expected: PASS with all tests passing.

- [ ] **Step 5: Commit changes**

```bash
git add config.example.yaml scripts/calendar_utils.py tests/test_calendar_utils.py
git commit -m "feat(calendar): support per-day working hours schema and update config template"
```

---

### Task 2: CLI Setup Wizard Streamlining (Remove NIP/NIK & Add Per-Day Hours)

**Files:**
- Modify: `main.py:53-85`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: interactive terminal inputs (Profile -> Period -> Schedule -> Work Hours default/custom -> Supervisor names).
- Produces: `run_setup_wizard(config_path)` saving `config.yaml` with per-day `jam_kerja` and supervisor dicts containing only `nama`.

- [ ] **Step 1: Update failing tests in `tests/test_main.py`**

Update `test_run_setup_wizard` and `test_run_setup_wizard_defaults` in `tests/test_main.py`:
- Remove inputs for NIP and NIK.
- Add input for work hours default choice (`Y` or `n`).
- Assert that `cfg["pembimbing"]["dosen"]` contains `nama` and NOT `nip`.
- Assert that `cfg["pembimbing"]["lapangan"]` contains `nama` and NOT `nik`.
- Assert that `cfg["pengaturan"]["jam_kerja"]` contains keys `senin` through `sabtu`.

```python
    @patch("builtins.input")
    def test_run_setup_wizard(self, mock_input):
        mock_input.side_effect = [
            "Ahmad Fauzi",
            "2241720005",
            "Sarjana Terapan Teknik Informatika",
            "PT Digital Inovasi",
            "2026-08-01",
            "2026-11-30",
            "1", # 5 hari
            "Y", # Jam kerja default
            "Dr. Dosen, M.Kom.",
            "Budi Santoso"
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_config.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["mahasiswa"]["nama"], "Ahmad Fauzi")
            self.assertEqual(cfg["periode"]["tanggal_mulai"], "2026-08-01")
            self.assertEqual(cfg["periode"]["tanggal_selesai"], "2026-11-30")
            self.assertEqual(cfg["pengaturan"]["hari_kerja"], "senin_jumat")
            self.assertIn("senin", cfg["pengaturan"]["jam_kerja"])
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["masuk"], "08.00")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["pulang"], "16.00")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["sabtu"]["pulang"], "14.00")
            self.assertEqual(cfg["pembimbing"]["dosen"], {"nama": "Dr. Dosen, M.Kom."})
            self.assertEqual(cfg["pembimbing"]["lapangan"], {"nama": "Budi Santoso"})
            self.assertNotIn("nip", cfg["pembimbing"]["dosen"])
            self.assertNotIn("nik", cfg["pembimbing"]["lapangan"])
            self.assertTrue(os.path.exists(cfg_path))

    @patch("builtins.input")
    def test_run_setup_wizard_defaults(self, mock_input):
        mock_input.side_effect = [
            "", # nama
            "", # nim
            "", # prodi
            "", # mitra
            "", # tgl_mulai
            "", # tgl_selesai
            "", # jadwal
            "", # jam kerja default (Enter = Y)
            "", # dosen
            ""  # mentor
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_default.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["mahasiswa"]["nama"], "Nama Mahasiswa")
            self.assertEqual(cfg["mahasiswa"]["nim"], "XXXXXXXXXX")
            self.assertEqual(cfg["periode"]["tanggal_mulai"], "2026-07-01")
            self.assertEqual(cfg["periode"]["tanggal_selesai"], "2026-12-31")
            self.assertEqual(cfg["pengaturan"]["hari_kerja"], "senin_sabtu")
            self.assertEqual(cfg["pembimbing"]["dosen"], {"nama": ""})
            self.assertEqual(cfg["pembimbing"]["lapangan"], {"nama": ""})
            self.assertNotIn("nip", cfg["pembimbing"]["dosen"])
            self.assertNotIn("nik", cfg["pembimbing"]["lapangan"])
            self.assertTrue(os.path.exists(cfg_path))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_main.py`
Expected: FAIL because `main.py` still expects NIP/NIK and does not prompt for jam kerja.

- [ ] **Step 3: Implement updated wizard logic in `main.py`**

In `main.py` inside `run_setup_wizard`:
Replace lines 53-78 with:
```python
    print("\nPilih Jadwal Kerja:")
    print("  1. 5 Hari Kerja (Senin - Jumat)")
    print("  2. 6 Hari Kerja (Senin - Sabtu)")
    jadwal_opt = input("Pilihan [2]: ").strip() or "2"
    hari_kerja = "senin_jumat" if jadwal_opt == "1" else "senin_sabtu"

    print("\nKonfigurasi Jam Kerja:")
    print("  Default: Senin-Jumat 08.00-16.00, Sabtu 08.00-14.00")
    use_default_hours = input("Gunakan jam kerja default? (Y/n) [Y]: ").strip().lower()
    if use_default_hours == "n":
        jam_masuk_week = input("  Jam Masuk (Senin - Jumat) [08.00]: ").strip() or "08.00"
        jam_pulang_week = input("  Jam Pulang (Senin - Jumat) [16.00]: ").strip() or "16.00"
        jam_masuk_sat = input("  Jam Masuk (Sabtu) [08.00]: ").strip() or "08.00"
        jam_pulang_sat = input("  Jam Pulang (Sabtu) [14.00]: ").strip() or "14.00"
    else:
        jam_masuk_week = "08.00"
        jam_pulang_week = "16.00"
        jam_masuk_sat = "08.00"
        jam_pulang_sat = "14.00"

    jam_kerja = {
        "senin": {"masuk": jam_masuk_week, "pulang": jam_pulang_week},
        "selasa": {"masuk": jam_masuk_week, "pulang": jam_pulang_week},
        "rabu": {"masuk": jam_masuk_week, "pulang": jam_pulang_week},
        "kamis": {"masuk": jam_masuk_week, "pulang": jam_pulang_week},
        "jumat": {"masuk": jam_masuk_week, "pulang": jam_pulang_week},
        "sabtu": {"masuk": jam_masuk_sat, "pulang": jam_pulang_sat},
    }

    nama_dosen = input("\nNama Dosen Pembimbing: ").strip() or ""
    nama_lapangan = input("Nama Pembimbing Lapangan (Mentor): ").strip() or ""

    config = {
        "mahasiswa": {"nama": nama, "nim": nim, "prodi": prodi, "mitra": mitra},
        "periode": {"tanggal_mulai": tgl_mulai, "tanggal_selesai": tgl_selesai},
        "pengaturan": {
            "hari_kerja": hari_kerja,
            "jam_kerja": jam_kerja,
        },
        "pembimbing": {
            "dosen": {"nama": nama_dosen},
            "lapangan": {"nama": nama_lapangan},
        },
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests/test_main.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add main.py tests/test_main.py
git commit -m "feat(cli): streamline setup wizard by removing NIP/NIK and adding per-day hours"
```

---

### Task 3: Web UI Backend Endpoints for Per-Day Hours & Streamlined Config

**Files:**
- Modify: `web/app.py`
- Test: `tests/test_web_api.py`

**Interfaces:**
- Consumes: `GET /api/calendar`, `POST /api/config` with per-day hours and supervisor names only.
- Produces: JSON payload preserving per-day hours in returned calendar day items (`d["jam_masuk"]`, `d["jam_pulang"]`).

- [ ] **Step 1: Write failing test in `tests/test_web_api.py`**

Add tests:
1. Update config with custom per-day hours (e.g. Jumat `08.00 - 11.30`) and supervisor without NIP/NIK.
2. Verify `/api/calendar` returns the custom Friday hours on Friday dates.
3. Verify `/api/config` does not require NIP/NIK.

```python
    def test_calendar_reflects_per_day_hours_and_streamlined_supervisor(self):
        cfg_res = self.client.get("/api/config")
        original_cfg = copy.deepcopy(cfg_res.json())
        try:
            cfg = copy.deepcopy(original_cfg)
            cfg.setdefault("pengaturan", {})["jam_kerja"] = {
                "senin": {"masuk": "08.00", "pulang": "16.00"},
                "selasa": {"masuk": "08.00", "pulang": "16.00"},
                "rabu": {"masuk": "08.00", "pulang": "16.00"},
                "kamis": {"masuk": "08.00", "pulang": "16.00"},
                "jumat": {"masuk": "08.00", "pulang": "11.30"},
                "sabtu": {"masuk": "08.00", "pulang": "14.00"},
            }
            cfg["pembimbing"] = {
                "dosen": {"nama": "Dosen Test, M.Kom."},
                "lapangan": {"nama": "Mentor Test"}
            }
            save_res = self.client.post("/api/config", json=cfg)
            self.assertEqual(save_res.status_code, 200)

            cal_res = self.client.get("/api/calendar")
            self.assertEqual(cal_res.status_code, 200)
            cal_data = cal_res.json()

            # Find a Friday in the calendar
            jumat_days = [
                d for m in cal_data["months"]
                for w in m["weeks"]
                for d in w["days"]
                if d["hari"] == "Jumat"
            ]
            self.assertTrue(len(jumat_days) > 0)
            self.assertEqual(jumat_days[0]["jam_masuk"], "08.00")
            self.assertEqual(jumat_days[0]["jam_pulang"], "11.30")
        finally:
            self.client.post("/api/config", json=original_cfg)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: Passes or fails depending on whether Task 1 is imported in `web/app.py`.

- [ ] **Step 3: Implement minimal verification in `web/app.py`**

Verify that `web/app.py` `get_calendar()` passes `config=config` to `get_internship_calendar(config=config)` and preserves `d["jam_masuk"]` and `d["jam_pulang"]`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_web_api.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add web/app.py tests/test_web_api.py
git commit -m "test(api): verify calendar endpoint reflects per-day hours and streamlined supervisor"
```

---

### Task 4: Frontend UI Redesign: Per-Day Hours Table, NIP/NIK Removal, & Hadir Auto-Hours

**Files:**
- Modify: `web/static/index.html:200-265`
- Modify: `web/static/styles.css`
- Modify: `web/static/app.js:200-360`
- Test: `tests/test_web_static.py`

**Interfaces:**
- Consumes: `#modal-config` form elements and `#editor-status` dropdown.
- Produces: Dynamic per-day hours table with Saturday row toggle, simplified supervisor fields, and automatic restore of working hours when status is `Hadir`.

- [ ] **Step 1: Write failing tests in `tests/test_web_static.py`**

Add tests asserting:
1. `cfg-dosen-nip` and `cfg-lapangan-nik` are NOT present in `index.html`.
2. `table-jam-kerja` and per-day inputs (`cfg-jam-senin-masuk`, `cfg-jam-jumat-pulang`, `row-jam-sabtu`) are present in `index.html`.
3. `styles.css` has styles for `.hours-table` and `.hidden-row`.
4. `app.js` contains logic to handle per-day hours and toggle the Saturday row based on schedule radio.

```python
    def test_hours_table_present_and_nip_nik_removed(self):
        res_html = self.client.get("/")
        self.assertEqual(res_html.status_code, 200)
        # NIP and NIK fields must be completely removed
        self.assertNotIn('id="cfg-dosen-nip"', res_html.text)
        self.assertNotIn('id="cfg-lapangan-nik"', res_html.text)
        # Per-day hours table must be present
        self.assertIn('id="table-jam-kerja"', res_html.text)
        self.assertIn('id="cfg-jam-senin-masuk"', res_html.text)
        self.assertIn('id="cfg-jam-senin-pulang"', res_html.text)
        self.assertIn('id="cfg-jam-jumat-pulang"', res_html.text)
        self.assertIn('id="row-jam-sabtu"', res_html.text)

        res_css = self.client.get("/static/styles.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn('.hours-table', res_css.text)
        self.assertIn('.hidden-row', res_css.text)

        res_js = self.client.get("/static/app.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn('table-jam-kerja', res_js.text)
        self.assertNotIn('cfgDosenNip', res_js.text)
        self.assertNotIn('cfgLapanganNik', res_js.text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: FAIL because `cfg-dosen-nip` and `cfg-lapangan-nik` still exist and `table-jam-kerja` does not.

- [ ] **Step 3: Implement changes in `web/static/index.html`, `styles.css`, and `app.js`**

1. In `web/static/index.html`:
Remove NIP and NIK columns. Convert supervisor names to full width:
```html
            <h4 class="section-title">Dosen Pembimbing (Kampus)</h4>
            <div class="form-group">
              <label class="form-label">Nama Dosen Pembimbing</label>
              <input type="text" id="cfg-dosen-nama" class="form-input" required>
            </div>

            <h4 class="section-title">Pembimbing Lapangan (Industri)</h4>
            <div class="form-group">
              <label class="form-label">Nama Pembimbing Lapangan</label>
              <input type="text" id="cfg-lapangan-nama" class="form-input" required>
            </div>
```

Add the Daily Working Hours Table inside `#modal-config` after `Jadwal Hari Kerja`:
```html
            <div class="form-group">
              <label class="form-label">Pengaturan Jam Kerja Harian</label>
              <div class="hours-table-wrapper">
                <table class="hours-table" id="table-jam-kerja">
                  <thead>
                    <tr>
                      <th>Hari</th>
                      <th>Jam Masuk</th>
                      <th>Jam Pulang</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr data-day="senin">
                      <td><span class="day-label">Senin</span></td>
                      <td><input type="text" id="cfg-jam-senin-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-senin-pulang" class="form-input form-input-sm" value="16.00" required></td>
                    </tr>
                    <tr data-day="selasa">
                      <td><span class="day-label">Selasa</span></td>
                      <td><input type="text" id="cfg-jam-selasa-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-selasa-pulang" class="form-input form-input-sm" value="16.00" required></td>
                    </tr>
                    <tr data-day="rabu">
                      <td><span class="day-label">Rabu</span></td>
                      <td><input type="text" id="cfg-jam-rabu-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-rabu-pulang" class="form-input form-input-sm" value="16.00" required></td>
                    </tr>
                    <tr data-day="kamis">
                      <td><span class="day-label">Kamis</span></td>
                      <td><input type="text" id="cfg-jam-kamis-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-kamis-pulang" class="form-input form-input-sm" value="16.00" required></td>
                    </tr>
                    <tr data-day="jumat">
                      <td><span class="day-label">Jumat</span></td>
                      <td><input type="text" id="cfg-jam-jumat-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-jumat-pulang" class="form-input form-input-sm" value="16.00" required></td>
                    </tr>
                    <tr data-day="sabtu" id="row-jam-sabtu">
                      <td><span class="day-label">Sabtu</span></td>
                      <td><input type="text" id="cfg-jam-sabtu-masuk" class="form-input form-input-sm" value="08.00" required></td>
                      <td><input type="text" id="cfg-jam-sabtu-pulang" class="form-input form-input-sm" value="14.00" required></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
```

2. In `web/static/styles.css`:
Add styles for `.hours-table-wrapper`, `.hours-table`, `.form-input-sm`, and `.hidden-row`:
```css
.hours-table-wrapper {
  overflow-x: auto;
  margin-top: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.hours-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}

.hours-table th,
.hours-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.hours-table th {
  background: var(--bg-card-hover);
  font-weight: 600;
  color: var(--text-muted);
}

.hours-table tr:last-child td {
  border-bottom: none;
}

.form-input-sm {
  padding: 0.35rem 0.5rem;
  font-size: 0.85rem;
  width: 100%;
  max-width: 110px;
}

.day-label {
  font-weight: 600;
  color: var(--text-color);
}

.hidden-row {
  display: none !important;
}
```

3. In `web/static/app.js`:
- In `dom` references:
  Remove `cfgDosenNip: document.getElementById('cfg-dosen-nip')` and `cfgLapanganNik: document.getElementById('cfg-lapangan-nik')`.
  Add `tableJamKerja: document.getElementById('table-jam-kerja')` and `rowJamSabtu: document.getElementById('row-jam-sabtu')`.
  Add constant `const DAYS_OF_WEEK = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu'];`
- Helper function `toggleSaturdayRow(schedule)`:
  ```javascript
  function toggleSaturdayRow(schedule) {
    if (dom.rowJamSabtu) {
      if (schedule === 'senin_jumat') {
        dom.rowJamSabtu.classList.add('hidden-row');
      } else {
        dom.rowJamSabtu.classList.remove('hidden-row');
      }
    }
  }
  ```
- In `loadConfigData()`:
  - Populate supervisor names:
    ```javascript
    dom.cfgDosenNama.value = dosen.nama || '';
    dom.cfgLapanganNama.value = lapangan.nama || '';
    ```
  - Populate per-day inputs:
    ```javascript
    const jamKerja = pengaturan.jam_kerja || {};
    const legacySj = jamKerja.senin_jumat || {};
    const legacySabtu = jamKerja.sabtu || {};

    DAYS_OF_WEEK.forEach(day => {
      const masukInput = document.getElementById(`cfg-jam-${day}-masuk`);
      const pulangInput = document.getElementById(`cfg-jam-${day}-pulang`);
      if (masukInput && pulangInput) {
        const daySpec = jamKerja[day] || (day === 'sabtu' ? legacySabtu : legacySj);
        masukInput.value = (daySpec && daySpec.masuk) || '08.00';
        pulangInput.value = (daySpec && daySpec.pulang) || (day === 'sabtu' ? '14.00' : '16.00');
      }
    });
    ```
  - Set schedule radio and call `toggleSaturdayRow(hariKerja)`.
- In `saveConfigData()`:
  - Build `jam_kerja` dictionary:
    ```javascript
    const jamKerjaPayload = {};
    DAYS_OF_WEEK.forEach(day => {
      const masukInput = document.getElementById(`cfg-jam-${day}-masuk`);
      const pulangInput = document.getElementById(`cfg-jam-${day}-pulang`);
      jamKerjaPayload[day] = {
        masuk: masukInput ? masukInput.value.trim() : '08.00',
        pulang: pulangInput ? pulangInput.value.trim() : (day === 'sabtu' ? '14.00' : '16.00')
      };
    });
    ```
  - Send supervisor without NIP/NIK:
    ```javascript
    pembimbing: {
      dosen: { nama: dom.cfgDosenNama.value.trim() },
      lapangan: { nama: dom.cfgLapanganNama.value.trim() }
    },
    pengaturan: {
      ...(existingCfg.pengaturan || {}),
      hari_kerja: selectedHariKerja,
      jam_kerja: jamKerjaPayload
    }
    ```
- In `initEvents()`:
  - Add event listener to `cfg-hari-kerja` radio inputs:
    ```javascript
    document.querySelectorAll('input[name="cfg-hari-kerja"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        toggleSaturdayRow(e.target.value);
      });
    });
    ```
- In `updateEditorStatusUI(status)`:
  - When status is `hadir`, automatically restore hours from `state.activeEditingDay`:
    ```javascript
    if (isHadir) {
      if (dom.editorHoursGroup) dom.editorHoursGroup.style.opacity = '1';
      if (state.activeEditingDay) {
        dom.editorHours.innerText = `${state.activeEditingDay.jam_masuk} - ${state.activeEditingDay.jam_pulang} WIB`;
      }
    ```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests/test_web_static.py`
Expected: PASS.

- [ ] **Step 5: Commit changes**

```bash
git add web/static/index.html web/static/styles.css web/static/app.js tests/test_web_static.py
git commit -m "feat(ui): add per-day hours table with Saturday toggle, hadir auto-hours, and remove NIP/NIK"
```

---

### Task 5: Full E2E & Documentation Verification

**Files:**
- Modify: `tests/test_e2e.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Complete CLI, Web UI, and LaTeX generation workflow with per-day hours.
- Produces: Verified PDF output with specific per-day hours reflected in text output and up-to-date documentation.

- [ ] **Step 1: Update `tests/test_e2e.py` with per-day hours build verification**

Add a test case `test_build_with_per_day_working_hours`:
```python
    @unittest.skipIf(shutil.which("pdftotext") is None, "pdftotext not installed")
    def test_build_with_per_day_working_hours(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_config = {
                "mahasiswa": {
                    "nama": "E2E Per Day Tester",
                    "nim": "1234567890",
                    "prodi": "D4 Teknik Informatika",
                    "mitra": "PT Daily Tech"
                },
                "periode": {
                    "tanggal_mulai": "2026-07-01",
                    "tanggal_selesai": "2026-07-04"
                },
                "pengaturan": {
                    "hari_kerja": "senin_sabtu",
                    "jam_kerja": {
                        "senin": {"masuk": "08.00", "pulang": "16.00"},
                        "selasa": {"masuk": "08.00", "pulang": "16.00"},
                        "rabu": {"masuk": "07.30", "pulang": "15.30"},
                        "kamis": {"masuk": "08.00", "pulang": "16.00"},
                        "jumat": {"masuk": "08.00", "pulang": "11.30"},
                        "sabtu": {"masuk": "08.30", "pulang": "13.00"},
                    }
                },
                "pembimbing": {
                    "dosen": {"nama": "Dosen Harian, M.Kom."},
                    "lapangan": {"nama": "Mentor Harian"}
                }
            }
            notes_map = {
                "2026-07-01": "Pengembangan modul per-hari",
                "2026-07-02": "Testing integrasi jam kerja",
                "2026-07-03": "Dokumentasi API per-hari",
                "2026-07-04": "Evaluasi mingguan jam kerja",
            }
            weeks = get_internship_calendar(config=test_config)
            out_pdf = os.path.join(tmp_dir, "test_per_day.pdf")
            tex_content = generate_latex_document(weeks, notes_map, test_config)
            compile_pdf(tex_content, out_pdf)

            self.assertTrue(os.path.exists(out_pdf))
            pdftotext_res = subprocess.run(
                ["pdftotext", out_pdf, "-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            text = pdftotext_res.stdout
            self.assertIn("07.30", text)
            self.assertIn("15.30", text)
            self.assertIn("11.30", text)
            self.assertIn("13.00", text)
            self.assertIn("Dosen Harian, M.Kom.", text)
            self.assertIn("Mentor Harian", text)
            self.assertNotIn("NIP.", text)
            self.assertNotIn("NIK.", text)
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python3 -m unittest tests/test_e2e.py`
Expected: PASS.

- [ ] **Step 3: Update `README.md` documentation**

Update `README.md`:
1. In the `config.yaml` example section, show the per-day `jam_kerja` dictionary (`senin` through `sabtu`) and streamlined `pembimbing` section without `nip` and `nik`.
2. In the Features section, highlight granular per-day working hours support and streamlined supervisor data.

- [ ] **Step 4: Run full test suite across all test files**

Run: `python3 -m unittest discover tests`
Expected: All tests pass with 0 failures and 0 errors.

- [ ] **Step 5: Commit changes**

```bash
git add tests/test_e2e.py README.md
git commit -m "docs: document per-day working hours and streamlined supervisor configuration"
```
