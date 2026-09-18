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
