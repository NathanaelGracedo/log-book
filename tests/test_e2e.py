# tests/test_e2e.py
import unittest
import os
import subprocess

class TestEndToEndBuild(unittest.TestCase):
    def test_build_month_1(self):
        # Build month 1
        res = subprocess.run(["python3", "main.py", "--month", "1", "--non-interactive"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
        
        pdf_path = "output/Logbook_01_Juli_2026.pdf"
        self.assertTrue(os.path.exists(pdf_path))

        # Verify page count: Month 1 has Weeks 1..5 -> exactly 5 pages
        pdfinfo_res = subprocess.run(["pdfinfo", pdf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdfinfo_res.returncode, 0, f"pdfinfo failed: {pdfinfo_res.stderr}")
        lines = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
        self.assertTrue(bool(lines), "Could not find Pages in pdfinfo output")
        pages = int(lines[0].split(":")[1].strip())
        self.assertEqual(pages, 5, f"Expected exactly 5 pages for Month 1, got {pages}")

        # Verify sample data is rendered in compiled PDF
        pdftotext_res = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(pdftotext_res.returncode, 0, f"pdftotext failed: {pdftotext_res.stderr}")
        self.assertIn("rekayasa perangkat lunak", pdftotext_res.stdout, "Sample data for July 1 not found in PDF")
        self.assertIn("evaluasi akhir pekan", pdftotext_res.stdout.lower(), "Sample data for Aug 1 (Week 5) not found in PDF")

if __name__ == "__main__":
    unittest.main()
