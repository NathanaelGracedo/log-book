import unittest
import os
import sys
import subprocess
import tempfile
from unittest.mock import patch
from main import (
    load_config,
    ensure_assets,
    build_pdf_bundle,
    run_setup_wizard,
    OUTPUT_MONTHLY_FILENAMES,
    CUMULATIVE_FILENAME,
)


class TestMainCLI(unittest.TestCase):
    def test_cli_help(self):
        res = subprocess.run([sys.executable, "main.py", "--help"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--month", res.stdout)
        self.assertIn("--check-only", res.stdout)
        self.assertIn("--all", res.stdout)
        self.assertIn("--cumulative-only", res.stdout)
        self.assertIn("--non-interactive", res.stdout)
        self.assertIn("--init", res.stdout)

    def test_check_only_flag(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_specific_month(self):
        res = subprocess.run(
            [sys.executable, "main.py", "-m", "1", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_cumulative_flag(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--cumulative-only", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_check_only_all_flag(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--all", "--check-only", "--non-interactive"],
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pemeriksaan tanggal selesai", res.stdout)

    def test_invalid_month_choice(self):
        res = subprocess.run(
            [sys.executable, "main.py", "-m", "7"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertNotEqual(res.returncode, 0)

    def test_mutually_exclusive_flags(self):
        res = subprocess.run(
            [sys.executable, "main.py", "-m", "1", "--all"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 2)
        self.assertIn("not allowed with argument", res.stderr)

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

    @patch("builtins.input")
    def test_run_setup_wizard(self, mock_input):
        mock_input.side_effect = [
            "Ahmad Fauzi",
            "2241720005",
            "Sarjana Terapan Teknik Informatika",
            "PT Digital Inovasi",
            "2026-08-01",
            "2026-11-30",
            "1", # 5 hari
            "Y", # Jam kerja default
            "Dr. Dosen, M.Kom.",
            "Budi Santoso"
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_config.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["mahasiswa"]["nama"], "Ahmad Fauzi")
            self.assertEqual(cfg["periode"]["tanggal_mulai"], "2026-08-01")
            self.assertEqual(cfg["periode"]["tanggal_selesai"], "2026-11-30")
            self.assertEqual(cfg["pengaturan"]["hari_kerja"], "senin_jumat")
            self.assertIn("senin", cfg["pengaturan"]["jam_kerja"])
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["masuk"], "08.00")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["pulang"], "16.00")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["sabtu"]["pulang"], "14.00")
            self.assertEqual(cfg["pembimbing"]["dosen"], {"nama": "Dr. Dosen, M.Kom."})
            self.assertEqual(cfg["pembimbing"]["lapangan"], {"nama": "Budi Santoso"})
            self.assertNotIn("nip", cfg["pembimbing"]["dosen"])
            self.assertNotIn("nik", cfg["pembimbing"]["lapangan"])
            self.assertTrue(os.path.exists(cfg_path))

    @patch("builtins.input")
    def test_run_setup_wizard_defaults(self, mock_input):
        mock_input.side_effect = [
            "", # nama
            "", # nim
            "", # prodi
            "", # mitra
            "", # tgl_mulai
            "", # tgl_selesai
            "", # jadwal
            "", # jam kerja default (Enter = Y)
            "", # dosen
            ""  # mentor
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_default.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["mahasiswa"]["nama"], "Nama Mahasiswa")
            self.assertEqual(cfg["mahasiswa"]["nim"], "XXXXXXXXXX")
            self.assertEqual(cfg["periode"]["tanggal_mulai"], "2026-07-01")
            self.assertEqual(cfg["periode"]["tanggal_selesai"], "2026-12-31")
            self.assertEqual(cfg["pengaturan"]["hari_kerja"], "senin_sabtu")
            self.assertEqual(cfg["pembimbing"]["dosen"], {"nama": ""})
            self.assertEqual(cfg["pembimbing"]["lapangan"], {"nama": ""})
            self.assertNotIn("nip", cfg["pembimbing"]["dosen"])
            self.assertNotIn("nik", cfg["pembimbing"]["lapangan"])
            self.assertTrue(os.path.exists(cfg_path))

    @patch("builtins.input")
    def test_run_setup_wizard_custom_hours(self, mock_input):
        mock_input.side_effect = [
            "Ahmad Fauzi",
            "2241720005",
            "Sarjana Terapan Teknik Informatika",
            "PT Digital Inovasi",
            "2026-08-01",
            "2026-11-30",
            "2", # 6 hari
            "n", # Custom jam kerja
            "07.30", # Masuk Senin-Jumat
            "16.30", # Pulang Senin-Jumat
            "08.00", # Masuk Sabtu
            "13.00", # Pulang Sabtu
            "Dr. Dosen, M.Kom.",
            "Budi Santoso"
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_path = os.path.join(tmp_dir, "test_wizard_custom.yaml")
            cfg = run_setup_wizard(cfg_path)
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["masuk"], "07.30")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["senin"]["pulang"], "16.30")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["jumat"]["masuk"], "07.30")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["jumat"]["pulang"], "16.30")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["sabtu"]["masuk"], "08.00")
            self.assertEqual(cfg["pengaturan"]["jam_kerja"]["sabtu"]["pulang"], "13.00")
            self.assertTrue(os.path.exists(cfg_path))

    @patch("main.run_setup_wizard")
    def test_cli_init_flag(self, mock_wizard):
        with patch.object(sys, "argv", ["main.py", "--init"]):
            with self.assertRaises(SystemExit) as cm:
                from main import main
                main()
            self.assertEqual(cm.exception.code, 0)
            mock_wizard.assert_called_once_with("config.yaml")

    @patch("main.init_data_files")
    @patch("main.check_missing_dates")
    @patch("main.load_all_notes")
    @patch("main.build_pdf_bundle")
    @patch("main.load_config")
    @patch("main.run_doctor")
    def test_dynamic_build_pipeline(self, mock_doctor, mock_load_config, mock_build_pdf, mock_load_notes, mock_check_missing, mock_init_files):
        # Configure a 3-month period: August to October 2026
        mock_load_config.return_value = {
            "mahasiswa": {"nama": "Test Mahasiswa", "nim": "12345", "prodi": "TI", "mitra": "Mitra"},
            "periode": {"tanggal_mulai": "2026-08-01", "tanggal_selesai": "2026-10-31"},
            "pengaturan": {"hari_kerja": "senin_jumat"}
        }
        mock_check_missing.return_value = []
        mock_load_notes.return_value = {}
        mock_build_pdf.return_value = "output/dummy.pdf"
        with patch.object(sys, "argv", ["main.py", "--all", "--non-interactive"]):
            from main import main
            main()

        # 3 monthly PDFs + 1 cumulative PDF = 4 calls
        self.assertEqual(mock_build_pdf.call_count, 4)
        out_names = [call[0][3] for call in mock_build_pdf.call_args_list]
        self.assertEqual(out_names[0], "Logbook_01_Agustus_2026.pdf")
        self.assertEqual(out_names[1], "Logbook_02_September_2026.pdf")
        self.assertEqual(out_names[2], "Logbook_03_Oktober_2026.pdf")
        self.assertEqual(out_names[3], "Logbook_Lengkap_Agustus_Oktober_2026.pdf")


if __name__ == "__main__":
    unittest.main()
