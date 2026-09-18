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
        yaml_files = [f for f in files if f.endswith(".yaml")]
        self.assertEqual(len(yaml_files), 6)
        expected_files = [
            "bulan_01_juli.yaml",
            "bulan_02_agustus.yaml",
            "bulan_03_september.yaml",
            "bulan_04_oktober.yaml",
            "bulan_05_november.yaml",
            "bulan_06_desember.yaml",
        ]
        for ef in expected_files:
            self.assertIn(ef, yaml_files)

    def test_init_does_not_overwrite_existing(self):
        d = datetime.date(2026, 7, 1)
        save_note_to_month(d, "catatan awal", self.data_dir)
        # Call init again
        init_data_files(self.data_dir)
        notes = load_all_notes(self.data_dir)
        self.assertEqual(notes.get("2026-07-01"), "catatan awal")

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

    def test_missing_dates_all_bundles(self):
        missing_all = check_missing_dates(None, self.data_dir)
        # Total calendar working days is 158
        self.assertEqual(len(missing_all), 158)

    def test_update_existing_note(self):
        d = datetime.date(2026, 7, 1)
        save_note_to_month(d, "catatan versi 1", self.data_dir)
        save_note_to_month(d, "catatan versi 2", self.data_dir)
        notes = load_all_notes(self.data_dir)
        self.assertEqual(notes["2026-07-01"], "catatan versi 2")

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

    def test_prompt_fill_missing_quit(self):
        missing = [datetime.date(2026, 7, 1), datetime.date(2026, 7, 2), datetime.date(2026, 7, 3)]
        inputs = iter(["task 1", "q"])
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
        self.assertNotIn("2026-07-03", notes)

    def test_prompt_fill_missing_interrupt(self):
        missing = [datetime.date(2026, 7, 1)]
        def raise_interrupt(p):
            raise KeyboardInterrupt()
        prompts = []
        filled = prompt_fill_missing(
            missing,
            input_func=raise_interrupt,
            print_func=lambda msg: prompts.append(msg),
            data_dir=self.data_dir
        )
        self.assertEqual(filled, 0)

    def test_prompt_fill_missing_empty_list(self):
        filled = prompt_fill_missing([], data_dir=self.data_dir)
        self.assertEqual(filled, 0)

if __name__ == "__main__":
    unittest.main()
