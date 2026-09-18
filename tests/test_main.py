import unittest
import os
import subprocess
from unittest.mock import patch
from main import (
    load_config,
    ensure_assets,
    build_pdf_bundle,
    OUTPUT_MONTHLY_FILENAMES,
    CUMULATIVE_FILENAME,
)


class TestMainCLI(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run(["python3", "main.py", "--help"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--month", res.stdout)
        self.assertIn("--check-only", res.stdout)
        self.assertIn("--all", res.stdout)
        self.assertIn("--cumulative-only", res.stdout)
        self.assertIn("--non-interactive", res.stdout)

    def test_check_only_flag(self):
        res = subprocess.run(
            ["python3", "main.py", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_specific_month(self):
        res = subprocess.run(
            ["python3", "main.py", "-m", "1", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_cumulative_flag(self):
        res = subprocess.run(
            ["python3", "main.py", "--cumulative-only", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_all_flag(self):
        res = subprocess.run(
            ["python3", "main.py", "--all", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_invalid_month_choice(self):
        res = subprocess.run(
            ["python3", "main.py", "-m", "7"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertNotEqual(res.returncode, 0)

    def test_load_config_valid(self):
        cfg = load_config("config.yaml")
        self.assertIn("mahasiswa", cfg)
        self.assertIn("pembimbing", cfg)

    def test_load_config_nonexistent(self):
        with self.assertRaises(FileNotFoundError):
            load_config("nonexistent_config_file.yaml")

    def test_ensure_assets(self):
        ensure_assets()
        self.assertTrue(os.path.exists("assets/polinema.png"))
        self.assertTrue(os.path.exists("assets/kemendikbud.jpg"))

    @patch("main.compile_pdf")
    @patch("main.generate_latex_document")
    def test_build_pdf_bundle_unit(self, mock_gen_latex, mock_compile):
        mock_gen_latex.return_value = "\\dummy{latex}"
        mock_compile.return_value = True

        dummy_weeks = [{"minggu_ke": 1, "days": []}]
        out = build_pdf_bundle(dummy_weeks, {}, {}, "test_bundle.pdf")

        self.assertEqual(out, os.path.join("output", "test_bundle.pdf"))
        mock_gen_latex.assert_called_once_with(dummy_weeks, {}, {})
        mock_compile.assert_called_once_with("\\dummy{latex}", os.path.join("output", "test_bundle.pdf"))

    def test_filenames_constants(self):
        self.assertEqual(len(OUTPUT_MONTHLY_FILENAMES), 6)
        self.assertEqual(OUTPUT_MONTHLY_FILENAMES[1], "Logbook_01_Juli_2026.pdf")
        self.assertEqual(OUTPUT_MONTHLY_FILENAMES[6], "Logbook_06_Desember_2026.pdf")
        self.assertEqual(CUMULATIVE_FILENAME, "Logbook_Lengkap_Juli_Desember_2026.pdf")


if __name__ == "__main__":
    unittest.main()
