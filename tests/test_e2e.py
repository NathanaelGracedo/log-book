import unittest
import os
import sys
import shutil
import subprocess
from scripts.data_manager import load_all_notes

class TestEndToEndBuild(unittest.TestCase):
    def test_build_month_1(self):
        # Build month 1
        res = subprocess.run(
            [sys.executable, "main.py", "--month", "1", "--non-interactive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        if not shutil.which("pdfinfo") or not shutil.which("pdftotext"):
            self.skipTest("poppler-utils (pdfinfo/pdftotext) not found on system")

        # Verify page count: Month 1 has Weeks 1..5 -> exactly 5 pages
        pdfinfo_res = subprocess.run(["pdfinfo", pdf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdfinfo_res.returncode, 0, f"pdfinfo failed: {pdfinfo_res.stderr}")
        lines = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
        self.assertTrue(bool(lines), "Could not find Pages in pdfinfo output")
        pages = int(lines[0].split(":")[1].strip())
        self.assertEqual(pages, 5, f"Expected exactly 5 pages for Month 1, got {pages}")

        # Extract text from PDF
        pdftotext_res = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdftotext_res.returncode, 0, f"pdftotext failed: {pdftotext_res.stderr}")
        pdf_text_lower = pdftotext_res.stdout.lower()

        # Invariant checks: Document title and institution
        self.assertIn("log book kegiatan", pdf_text_lower)
        self.assertIn("politeknik negeri malang", pdf_text_lower)
        self.assertIn("jurusan teknologi informasi", pdf_text_lower)

        # Dynamic check: Verify that July 1 note from data/ is rendered
        notes_map = load_all_notes("data")
        july_1_note = notes_map.get("2026-07-01", "").strip()
        if july_1_note:
            # Check the first 20 characters of the recorded note to avoid line wrap / expansion discrepancy
            sample_phrase = july_1_note.split()[0].lower()
            self.assertIn(sample_phrase, pdf_text_lower, f"Expected note keyword '{sample_phrase}' in PDF output")

    def test_build_with_status_and_new_signature(self):
        # Build month 1
        res = subprocess.run(
            [sys.executable, "main.py", "--month", "1", "--non-interactive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"Build failed: {res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext not found")

        pdftotext_res = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, text=True)
        out_text = pdftotext_res.stdout.lower()

        # Invariant checks
        self.assertIn("log book kegiatan", out_text)
        self.assertIn("mengetahui", out_text)
        self.assertIn("dosen pembimbing", out_text)
        self.assertIn("pembimbing lapangan", out_text)
        # Ensure NIM., NIP., NIK. are not in the signature block
        self.assertNotIn("nim.", out_text)
        self.assertNotIn("nip.", out_text)
        self.assertNotIn("nik.", out_text)

if __name__ == "__main__":
    unittest.main()


