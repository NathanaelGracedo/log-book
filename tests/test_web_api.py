# tests/test_web_api.py
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import tempfile
import os
import shutil
import yaml
import copy

class TestWebApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Backup data and config files to avoid dirtying git workspace
        cls._backup_dir = tempfile.mkdtemp(prefix="test_web_backup_")
        if os.path.exists("data"):
            shutil.copytree("data", os.path.join(cls._backup_dir, "data"))
        if os.path.exists("config.yaml"):
            shutil.copy("config.yaml", os.path.join(cls._backup_dir, "config.yaml"))

        from web.app import app
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Restore data and config files
        if hasattr(cls, "_backup_dir") and os.path.exists(cls._backup_dir):
            data_backup = os.path.join(cls._backup_dir, "data")
            if os.path.exists(data_backup):
                if os.path.exists("data"):
                    shutil.rmtree("data")
                shutil.copytree(data_backup, "data")
            config_backup = os.path.join(cls._backup_dir, "config.yaml")
            if os.path.exists(config_backup):
                shutil.copy(config_backup, "config.yaml")
            shutil.rmtree(cls._backup_dir, ignore_errors=True)

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

    def test_save_day_invalid_date(self):
        res = self.client.post("/api/save-day", json={"date": "invalid-date", "note": "Testing"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("detail", res.json())

    def test_batch_autofill_endpoint(self):
        with patch("web.app.batch_autofill_notes", return_value=(10, 20)) as mock_autofill:
            res = self.client.post("/api/batch-autofill", json={"overwrite_existing": False})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["filled_count"], 10)
            mock_autofill.assert_called_once_with(overwrite_existing=False, data_dir="data")

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
        original_cfg = copy.deepcopy(cfg_res.json())
        try:
            cfg = copy.deepcopy(original_cfg)
            cfg.setdefault("pengaturan", {})["hari_kerja"] = "senin_jumat"
            self.client.post("/api/config", json=cfg)

            cal_res = self.client.get("/api/calendar")
            self.assertEqual(cal_res.status_code, 200)
            cal_data = cal_res.json()
            # Ensure no Saturday in returned calendar days
            for m in cal_data["months"]:
                for w in m["weeks"]:
                    for d in w["days"]:
                        self.assertNotEqual(d["hari"], "Sabtu")
        finally:
            self.client.post("/api/config", json=original_cfg)

    def test_calendar_day_fields(self):
        # Save a day with status
        self.client.post("/api/save-day", json={"date": "2026-07-03", "status": "izin", "note": "Keperluan keluarga"})
        cal_res = self.client.get("/api/calendar")
        self.assertEqual(cal_res.status_code, 200)
        cal_data = cal_res.json()
        found = False
        for m in cal_data["months"]:
            for w in m["weeks"]:
                for d in w["days"]:
                    self.assertIn("attendance_status", d)
                    self.assertIn("kegiatan", d)
                    if d["date_str"] == "2026-07-03":
                        self.assertEqual(d["attendance_status"], "izin")
                        self.assertEqual(d["kegiatan"], "Keperluan keluarga")
                        self.assertTrue(d["is_filled"])
                        found = True
        self.assertTrue(found)

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

    def test_generate_pdf_endpoint(self):
        with patch("web.app.build_pdf_bundle", return_value="output/dummy.pdf") as mock_build:
            # Test single month target
            res = self.client.post("/api/generate-pdf", json={"target": 1})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "ok")
            self.assertIn("pdf_url", res.json())

            # Test cumulative target
            res_cum = self.client.post("/api/generate-pdf", json={"target": "cumulative"})
            self.assertEqual(res_cum.status_code, 200)
            self.assertEqual(res_cum.json()["status"], "ok")

            # Test all target
            res_all = self.client.post("/api/generate-pdf", json={"target": "all"})
            self.assertEqual(res_all.status_code, 200)
            self.assertEqual(res_all.json()["status"], "ok")
            self.assertIn("all_urls", res_all.json())

if __name__ == "__main__":
    unittest.main()

