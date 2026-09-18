# tests/test_latex_builder.py
import unittest
import os
import tempfile
import datetime
import subprocess
from scripts.latex_builder import generate_latex_document, compile_pdf

class TestLatexBuilder(unittest.TestCase):
    def setUp(self):
        self.config = {
            "mahasiswa": {
                "nama": "Budi Santoso",
                "nim": "2241720001",
                "prodi": "Sarjana Terapan Teknik Informatika",
                "mitra": "PT Naraya Telematika"
            },
            "pembimbing": {
                "dosen": {"nama": "Dr. Ir. Pembimbing, M.Kom.", "nip": "198001012005011001"},
                "lapangan": {"nama": "Senior Engineer", "nik": "EMP-1002"}
            }
        }
        self.weeks = [
            {
                "minggu_ke": 1,
                "days": [
                    {
                        "date": datetime.date(2026, 7, 1),
                        "date_str": "2026-07-01",
                        "hari": "Rabu",
                        "tanggal_str": "1 Juli 2026",
                        "jam_masuk": "08.00",
                        "jam_pulang": "16.00"
                    }
                ]
            },
            {
                "minggu_ke": 2,
                "days": [
                    {
                        "date": datetime.date(2026, 7, 8),
                        "date_str": "2026-07-08",
                        "hari": "Rabu",
                        "tanggal_str": "8 Juli 2026",
                        "jam_masuk": "08.00",
                        "jam_pulang": "16.00"
                    }
                ]
            }
        ]
        self.notes_map = {
            "2026-07-01": "Mengikuti onboarding & instalasi software kerja.",
            "2026-07-08": "Melakukan implementasi fitur modul autentikasi."
        }

    def test_generate_latex_contains_required_fields(self):
        latex = generate_latex_document(self.weeks, self.notes_map, self.config)
        self.assertIn("Budi Santoso", latex)
        self.assertIn("2241720001", latex)
        self.assertIn("PT Naraya Telematika", latex)
        self.assertIn("Mengikuti onboarding \\& instalasi software kerja.", latex)
        self.assertIn("LOG BOOK KEGIATAN", latex)
        self.assertIn(r"\clearpage", latex)

    def test_single_week_no_clearpage(self):
        single_week = [self.weeks[0]]
        latex = generate_latex_document(single_week, self.notes_map, self.config)
        self.assertIn("Budi Santoso", latex)
        self.assertNotIn(r"\clearpage", latex)

    def test_compile_pdf(self):
        latex = generate_latex_document(self.weeks, self.notes_map, self.config)
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = os.path.join(tmp_dir, "test_output.pdf")
            success = compile_pdf(latex, out_pdf)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_pdf))
            self.assertGreater(os.path.getsize(out_pdf), 0)

            # Verify page count is exactly 2 for 2 weeks
            pdfinfo_res = subprocess.run(["pdfinfo", out_pdf], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if pdfinfo_res.returncode == 0:
                pages_line = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
                if pages_line:
                    pages = int(pages_line[0].split(":")[1].strip())
                    self.assertEqual(pages, 2)

    def test_full_six_day_week_fits_single_page(self):
        six_day_week = [{
            "minggu_ke": 3,
            "days": [
                {"date": datetime.date(2026, 7, 6), "date_str": "2026-07-06", "hari": "Senin", "tanggal_str": "6 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "16.00"},
                {"date": datetime.date(2026, 7, 7), "date_str": "2026-07-07", "hari": "Selasa", "tanggal_str": "7 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "16.00"},
                {"date": datetime.date(2026, 7, 8), "date_str": "2026-07-08", "hari": "Rabu", "tanggal_str": "8 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "16.00"},
                {"date": datetime.date(2026, 7, 9), "date_str": "2026-07-09", "hari": "Kamis", "tanggal_str": "9 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "16.00"},
                {"date": datetime.date(2026, 7, 10), "date_str": "2026-07-10", "hari": "Jumat", "tanggal_str": "10 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "16.00"},
                {"date": datetime.date(2026, 7, 11), "date_str": "2026-07-11", "hari": "Sabtu", "tanggal_str": "11 Juli 2026", "jam_masuk": "08.00", "jam_pulang": "14.00"},
            ]
        }]
        notes_map = {
            "2026-07-06": "meeting mingguan sprint planning dan pembagian tiket tugas fitur manajemen pengguna",
            "2026-07-07": "implementasi endpoint autentikasi jwt pada modul login sistem backend api",
            "2026-07-08": "coding validasi input form dan sanitasi data payload request transaksi",
            "2026-07-09": "testing integrasi endpoint autentikasi menggunakan postman dan automated testing",
            "2026-07-10": "bugfix penanganan token expired pada middleware otorisasi serta perbaikan log format",
            "2026-07-11": "dokumentasi teknis alur autentikasi pada wiki repositori dan review mingguan",
        }
        latex = generate_latex_document(six_day_week, notes_map, self.config)
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = os.path.join(tmp_dir, "test_six_days.pdf")
            success = compile_pdf(latex, out_pdf)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_pdf))

            # Must fit on exactly 1 page
            pdfinfo_res = subprocess.run(["pdfinfo", out_pdf], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(pdfinfo_res.returncode, 0)
            pages_line = [l for l in pdfinfo_res.stdout.splitlines() if "Pages:" in l]
            self.assertTrue(len(pages_line) > 0)
            pages = int(pages_line[0].split(":")[1].strip())
            self.assertEqual(pages, 1, f"Expected 1 page for 6-day week, but got {pages}")

if __name__ == "__main__":
    unittest.main()
