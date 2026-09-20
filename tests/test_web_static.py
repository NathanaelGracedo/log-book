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

    def test_serve_static_asset(self):
        res = self.client.get("/static/index.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))

    def test_serve_styles_css(self):
        res = self.client.get("/static/styles.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/css", res.headers.get("content-type", ""))
        self.assertIn("--primary:", res.text)
        self.assertIn("[data-theme=\"dark\"]", res.text)

    def test_serve_app_js(self):
        res = self.client.get("/static/app.js")
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.headers.get("content-type", ""))
        self.assertIn("fetchCalendar", res.text)
        self.assertIn("formalizeNote", res.text)

    def test_attendance_and_period_elements_present_in_static_files(self):
        res_html = self.client.get("/")
        self.assertEqual(res_html.status_code, 200)
        self.assertIn('id="editor-status"', res_html.text)
        self.assertIn('id="cfg-periode-mulai"', res_html.text)
        self.assertIn('id="cfg-periode-selesai"', res_html.text)
        self.assertIn('name="cfg-hari-kerja"', res_html.text)
        self.assertIn('value="hadir"', res_html.text)
        self.assertIn('value="izin"', res_html.text)
        self.assertIn('value="sakit"', res_html.text)
        self.assertIn('value="cuti"', res_html.text)
        self.assertIn('value="libur"', res_html.text)
        self.assertIn('value="senin_sabtu"', res_html.text)
        self.assertIn('value="senin_jumat"', res_html.text)

        res_css = self.client.get("/static/styles.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn('.badge-izin', res_css.text)
        self.assertIn('.badge-sakit', res_css.text)
        self.assertIn('.badge-cuti', res_css.text)
        self.assertIn('.badge-libur', res_css.text)
        self.assertIn('.text-danger', res_css.text)

    def test_app_js_attendance_and_config(self):
        res_js = self.client.get("/static/app.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertIn('editorStatus', res_js.text)
        self.assertIn('badge-izin', res_js.text)
        self.assertIn('text-danger', res_js.text)
        self.assertIn('cfgPeriodeMulai', res_js.text)
        self.assertIn('cfg-hari-kerja', res_js.text)

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

if __name__ == "__main__":
    unittest.main()


