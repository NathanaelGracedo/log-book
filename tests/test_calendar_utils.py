import unittest
import datetime
from scripts.calendar_utils import (
    get_internship_calendar,
    get_calendar_working_days,
    get_month_bundle_weeks,
    get_yaml_filename_for_date,
    MONTH_BUNDLE_WEEKS,
    format_indonesian_date,
)

class TestCalendarUtils(unittest.TestCase):
    def test_total_weeks_and_bounds(self):
        weeks = get_internship_calendar()
        self.assertEqual(len(weeks), 27)
        # Week 1 starts 2026-07-01 (Wed) and ends 2026-07-04 (Sat) (4 days)
        w1 = weeks[0]
        self.assertEqual(w1["minggu_ke"], 1)
        self.assertEqual(len(w1["days"]), 4)
        self.assertEqual(w1["days"][0]["date"], datetime.date(2026, 7, 1))
        self.assertEqual(w1["days"][0]["hari"], "Rabu")
        self.assertEqual(w1["days"][0]["jam_masuk"], "08.00")
        self.assertEqual(w1["days"][0]["jam_pulang"], "16.00")
        self.assertEqual(w1["days"][3]["hari"], "Sabtu")
        self.assertEqual(w1["days"][3]["jam_pulang"], "14.00")

        # Week 27 ends 2026-12-31 (Thu) (4 days)
        w27 = weeks[26]
        self.assertEqual(w27["minggu_ke"], 27)
        self.assertEqual(len(w27["days"]), 4)
        self.assertEqual(w27["days"][-1]["date"], datetime.date(2026, 12, 31))
        self.assertEqual(w27["days"][-1]["hari"], "Kamis")
        self.assertEqual(w27["days"][-1]["jam_pulang"], "16.00")

        # Total working days across all 27 weeks should equal 158
        total_days = sum(len(w["days"]) for w in weeks)
        self.assertEqual(total_days, 158)

    def test_working_days_per_calendar_month(self):
        # Total active working days July - Dec: 158 days
        all_days = get_calendar_working_days(None)
        self.assertEqual(len(all_days), 158)
        # July: 31 days - 4 Sundays = 27 days
        july_days = get_calendar_working_days(7)
        self.assertEqual(len(july_days), 27)
        # August: 31 days - 5 Sundays = 26 days
        aug_days = get_calendar_working_days(8)
        self.assertEqual(len(aug_days), 26)
        # September: 30 days - 4 Sundays = 26 days
        sep_days = get_calendar_working_days(9)
        self.assertEqual(len(sep_days), 26)
        # October: 31 days - 4 Sundays = 27 days
        oct_days = get_calendar_working_days(10)
        self.assertEqual(len(oct_days), 27)
        # November: 30 days - 5 Sundays = 25 days
        nov_days = get_calendar_working_days(11)
        self.assertEqual(len(nov_days), 25)
        # December: 31 days - 4 Sundays = 27 days
        dec_days = get_calendar_working_days(12)
        self.assertEqual(len(dec_days), 27)

    def test_month_bundles(self):
        # Bundle 1 (July): Weeks 1-5 (5 weeks)
        b1 = get_month_bundle_weeks(1)
        self.assertEqual(len(b1), 5)
        self.assertEqual(b1[0]["minggu_ke"], 1)
        self.assertEqual(b1[-1]["minggu_ke"], 5)

        # Bundle 2 (August): Weeks 6-9 (4 weeks)
        b2 = get_month_bundle_weeks(2)
        self.assertEqual(len(b2), 4)
        self.assertEqual(b2[0]["minggu_ke"], 6)
        self.assertEqual(b2[-1]["minggu_ke"], 9)

        # Check all 6 bundles coverage
        all_bundle_weeks = []
        for i in range(1, 7):
            bundle = get_month_bundle_weeks(i)
            all_bundle_weeks.extend([w["minggu_ke"] for w in bundle])
        self.assertEqual(all_bundle_weeks, list(range(1, 28)))

        # Invalid bundle index raises ValueError
        with self.assertRaises(ValueError):
            get_month_bundle_weeks(0)
        with self.assertRaises(ValueError):
            get_month_bundle_weeks(7)

    def test_yaml_filename_mapping(self):
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 7, 15)), "bulan_01_juli.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 8, 1)), "bulan_02_agustus.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 9, 30)), "bulan_03_september.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 10, 10)), "bulan_04_oktober.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 11, 20)), "bulan_05_november.yaml")
        self.assertEqual(get_yaml_filename_for_date(datetime.date(2026, 12, 31)), "bulan_06_desember.yaml")

        # Outside bounds raises ValueError
        with self.assertRaises(ValueError):
            get_yaml_filename_for_date(datetime.date(2026, 6, 30))
        with self.assertRaises(ValueError):
            get_yaml_filename_for_date(datetime.date(2027, 1, 1))

    def test_format_indonesian_date(self):
        self.assertEqual(format_indonesian_date(datetime.date(2026, 7, 1)), "1 Juli 2026")
        self.assertEqual(format_indonesian_date(datetime.date(2026, 12, 31)), "31 Desember 2026")

if __name__ == "__main__":
    unittest.main()
