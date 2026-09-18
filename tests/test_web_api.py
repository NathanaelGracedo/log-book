# tests/test_web_api.py
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import tempfile
import os
import shutil
import yaml

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
