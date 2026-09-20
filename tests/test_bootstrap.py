# tests/test_bootstrap.py
import unittest
import os
import shutil
import tempfile
import yaml
from main import load_config

class TestConfigBootstrap(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_bootstrap_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bootstrap_copies_example_when_config_missing(self):
        example_path = os.path.join(self.temp_dir, "config.example.yaml")
        config_path = os.path.join(self.temp_dir, "config.yaml")

        example_data = {
            "mahasiswa": {
                "nama": "Nama Lengkap Mahasiswa",
                "nim": "XXXXXXXXXX",
                "prodi": "Sarjana Terapan Teknik Informatika",
                "mitra": "Nama Perusahaan / Tempat Magang"
            },
            "pembimbing": {
                "dosen": {"nama": "Nama Dosen", "nip": "198000000000"},
                "lapangan": {"nama": "Nama Pembimbing Lapangan", "nik": "EMP-001"}
            },
            "pengaturan": {
                "jam_kerja": {
                    "senin_jumat": {"masuk": "08.00", "pulang": "16.00"},
                    "sabtu": {"masuk": "08.00", "pulang": "14.00"}
                }
            }
        }
        with open(example_path, "w", encoding="utf-8") as f:
            yaml.dump(example_data, f)

        # Call load_config with missing config_path and existing example_path
        loaded = load_config(config_path=config_path, example_path=example_path)
        self.assertTrue(os.path.exists(config_path))
        self.assertEqual(loaded["mahasiswa"]["nama"], "Nama Lengkap Mahasiswa")

    def test_load_config_raises_when_both_missing(self):
        config_path = os.path.join(self.temp_dir, "non_existent.yaml")
        example_path = os.path.join(self.temp_dir, "non_existent_example.yaml")
        with self.assertRaises(FileNotFoundError):
            load_config(config_path=config_path, example_path=example_path)

if __name__ == "__main__":
    unittest.main()
