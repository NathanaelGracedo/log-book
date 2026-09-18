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

    def test_batch_autofill_with_overwrite(self):
        tmp_dir = tempfile.mkdtemp(prefix="test_curriculum_overwrite_")
        try:
            july_file = os.path.join(tmp_dir, "bulan_01_juli.yaml")
            os.makedirs(tmp_dir, exist_ok=True)
            with open(july_file, "w", encoding="utf-8") as f:
                yaml.dump({
                    "bulan": 7,
                    "tahun": 2026,
                    "catatan": {
                        "2026-07-01": "Catatan manual lama"
                    }
                }, f)

            filled, total_missing = batch_autofill_notes(overwrite_existing=True, data_dir=tmp_dir)
            self.assertEqual(filled, 158)
            self.assertEqual(total_missing, 157)

            with open(july_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self.assertNotEqual(data["catatan"]["2026-07-01"], "Catatan manual lama")
            self.assertIn("onboarding", data["catatan"]["2026-07-01"].lower())
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
