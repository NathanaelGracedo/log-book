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

if __name__ == "__main__":
    unittest.main()
