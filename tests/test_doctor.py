# tests/test_doctor.py
import unittest
from unittest.mock import patch
from scripts.doctor import check_xelatex, run_doctor

class TestDoctor(unittest.TestCase):
    @patch("shutil.which")
    def test_check_xelatex_found(self, mock_which):
        mock_which.return_value = "/usr/bin/xelatex"
        found, info = check_xelatex()
        self.assertTrue(found)
        self.assertEqual(info, "/usr/bin/xelatex")

    @patch("shutil.which")
    def test_check_xelatex_missing(self, mock_which):
        mock_which.return_value = None
        found, instructions = check_xelatex()
        self.assertFalse(found)
        # Should include install guidance for major OS platforms
        self.assertIn("apt install texlive-xetex", instructions)
        self.assertIn("pacman -S", instructions)
        self.assertIn("dnf install", instructions)
        self.assertIn("brew install", instructions)
        self.assertIn("MiKTeX", instructions)

    @patch("scripts.doctor.check_xelatex")
    def test_run_doctor_exit_on_failure(self, mock_check):
        mock_check.return_value = (False, "Instalasi xelatex diperlukan")
        with self.assertRaises(SystemExit) as cm:
            run_doctor(exit_on_failure=True)
        self.assertEqual(cm.exception.code, 1)

    @patch("scripts.doctor.check_xelatex")
    def test_run_doctor_no_exit_on_failure(self, mock_check):
        mock_check.return_value = (False, "Instalasi xelatex diperlukan")
        res = run_doctor(exit_on_failure=False)
        self.assertFalse(res)

    @patch("scripts.doctor.check_xelatex")
    def test_run_doctor_success(self, mock_check):
        mock_check.return_value = (True, "/usr/bin/xelatex")
        self.assertTrue(run_doctor(exit_on_failure=True))

    @patch("main.run_doctor")
    @patch("main.ensure_assets")
    @patch("main.init_data_files")
    def test_main_runs_doctor_when_not_check_only(self, mock_init, mock_assets, mock_run_doctor):
        import sys
        import main
        with patch.object(sys, "argv", ["main.py", "--ui"]):
            with patch("uvicorn.run"):
                with self.assertRaises(SystemExit):
                    main.main()
        mock_run_doctor.assert_called_once_with(exit_on_failure=True)

    @patch("main.run_doctor")
    @patch("main.ensure_assets")
    @patch("main.init_data_files")
    def test_main_skips_doctor_when_check_only(self, mock_init, mock_assets, mock_run_doctor):
        import sys
        import main
        with patch.object(sys, "argv", ["main.py", "--check-only", "--non-interactive"]):
            with self.assertRaises(SystemExit):
                main.main()
        mock_run_doctor.assert_not_called()

if __name__ == "__main__":
    unittest.main()
