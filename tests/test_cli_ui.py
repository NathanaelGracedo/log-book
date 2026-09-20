# tests/test_cli_ui.py
import unittest
import subprocess
import sys
from unittest.mock import patch


class TestCliUiFlag(unittest.TestCase):
    def test_cli_help_includes_ui_flag(self):
        res = subprocess.run([sys.executable, "main.py", "--help"], stdout=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--ui", res.stdout)
        self.assertIn("dashboard", res.stdout.lower())

    @patch("uvicorn.run")
    @patch("main.ensure_assets")
    @patch("main.init_data_files")
    def test_cli_ui_launches_uvicorn(self, mock_init, mock_assets, mock_uvicorn):
        import main
        with patch.object(sys, "argv", ["main.py", "--ui", "--host", "0.0.0.0", "--port", "9000"]):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)
            mock_assets.assert_called_once()
            mock_init.assert_called_once_with("data", main.load_config("config.yaml"))
            mock_uvicorn.assert_called_once_with("web.app:app", host="0.0.0.0", port=9000, reload=False)


if __name__ == "__main__":
    unittest.main()
