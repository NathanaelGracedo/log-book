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

        # Invalid target validation
        res_invalid = self.client.post("/api/generate-pdf", json={"target": 99})
        self.assertEqual(res_invalid.status_code, 400)
        self.assertIn("detail", res_invalid.json())

    @patch("web.app.build_pdf_bundle")
    def test_generate_pdf_cumulative(self, mock_build):
        mock_build.return_value = "output/Logbook_Lengkap_Juli_Desember_2026.pdf"
        res = self.client.post("/api/generate-pdf", json={"target": "cumulative"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("Logbook_Lengkap_Juli_Desember_2026.pdf", data["pdf_url"])

        # Target 'all' compiles 6 months + 1 cumulative
        mock_build.reset_mock()
        res_all = self.client.post("/api/generate-pdf", json={"target": "all"})
        self.assertEqual(res_all.status_code, 200)
        data_all = res_all.json()
        self.assertEqual(data_all["status"], "ok")
        self.assertEqual(len(data_all["all_urls"]), 7)
        self.assertEqual(mock_build.call_count, 7)

    def test_stream_pdf_nonexistent(self):
        res = self.client.get("/api/pdf/nonexistent_file.pdf")
        self.assertEqual(res.status_code, 404)

        # Stream existing file
        if os.path.exists(os.path.join("output", "Logbook_01_Juli_2026.pdf")):
            res_ok = self.client.get("/api/pdf/Logbook_01_Juli_2026.pdf")
            self.assertEqual(res_ok.status_code, 200)
            self.assertEqual(res_ok.headers["content-type"], "application/pdf")
            self.assertIn("inline", res_ok.headers.get("content-disposition", ""))

    def test_stream_pdf_directory_traversal_attack(self):
        res = self.client.get("/api/pdf/../../etc/passwd")
        self.assertIn(res.status_code, [400, 404])
        res2 = self.client.get("/api/pdf/subdir/file.pdf")
        self.assertIn(res2.status_code, [400, 404])

if __name__ == "__main__":
    unittest.main()
