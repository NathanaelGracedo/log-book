# scripts/calendar_utils.py
import datetime

INDONESIAN_DAYS: dict[int, str] = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

INDONESIAN_MONTHS: dict[int, str] = {
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

# Mapping of month report index (1..6) to (start_week, end_week)
MONTH_BUNDLE_WEEKS: dict[int, tuple[int, int]] = {
    1: (1, 5),    # Juli
    2: (6, 9),    # Agustus
    3: (10, 14),  # September
    4: (15, 18),  # Oktober
    5: (19, 22),  # November
    6: (23, 27),  # Desember
}

START_DATE = datetime.date(2026, 7, 1)
END_DATE = datetime.date(2026, 12, 31)

def format_indonesian_date(d: datetime.date) -> str:
    """Returns date in format: 1 Juli 2026"""
    month_name = INDONESIAN_MONTHS.get(d.month, str(d.month))
    return f"{d.day} {month_name} {d.year}"

def get_calendar_working_days(month_num: int | None = None) -> list[datetime.date]:
    """Returns all Monday-Saturday dates within the internship period or for a specific month (7..12)."""
    curr = START_DATE
    days = []
    while curr <= END_DATE:
        if curr.weekday() != 6:  # Skip Sunday
            if month_num is None or curr.month == month_num:
                days.append(curr)
        curr += datetime.timedelta(days=1)
    return days

def get_internship_calendar() -> list[dict]:
    """
    Partitions the internship period (2026-07-01 to 2026-12-31) into 27 weeks.
    Each week contains a list of day dictionaries:
      - date: datetime.date
      - date_str: "YYYY-MM-DD"
      - hari: "Senin", "Selasa", etc.
      - tanggal_str: "1 Juli 2026"
      - jam_masuk: "08.00"
      - jam_pulang: "16.00" (or "14.00" for Sabtu)
    """
    weeks = []
    current_days = []
    curr = START_DATE
    week_num = 1

    while curr <= END_DATE:
        if curr.weekday() != 6:
            hari = INDONESIAN_DAYS[curr.weekday()]
            jam_masuk = "08.00"
            jam_pulang = "14.00" if curr.weekday() == 5 else "16.00"
            day_info = {
                "date": curr,
                "date_str": curr.strftime("%Y-%m-%d"),
                "hari": hari,
                "tanggal_str": format_indonesian_date(curr),
                "jam_masuk": jam_masuk,
                "jam_pulang": jam_pulang,
            }
            current_days.append(day_info)

        # A week ends on Saturday or on the final day (Thursday Dec 31)
        if curr.weekday() == 5 or curr == END_DATE:
            if current_days:
                weeks.append({
                    "minggu_ke": week_num,
                    "days": current_days
                })
                week_num += 1
                current_days = []

        curr += datetime.timedelta(days=1)

    return weeks

def get_month_bundle_weeks(bundle_index: int) -> list[dict]:
    """Returns the list of weeks belonging to a specific monthly report bundle (1..6)."""
    if bundle_index not in MONTH_BUNDLE_WEEKS:
        raise ValueError(f"Bundle index must be between 1 and 6, got {bundle_index}")
    
    start_wk, end_wk = MONTH_BUNDLE_WEEKS[bundle_index]
    all_weeks = get_internship_calendar()
    return [w for w in all_weeks if start_wk <= w["minggu_ke"] <= end_wk]

def get_yaml_filename_for_date(d: datetime.date) -> str:
    """Maps a given date to its corresponding YAML filename based on month."""
    if d < START_DATE or d > END_DATE:
        raise ValueError(f"Date {d} is outside the internship period (July-December 2026)")
    month_names = {
        7: "01_juli",
        8: "02_agustus",
        9: "03_september",
        10: "04_oktober",
        11: "05_november",
        12: "06_desember"
    }
    suffix = month_names.get(d.month)
    if not suffix:
        raise ValueError(f"Date {d} is outside the internship period (July-December 2026)")
    return f"bulan_{suffix}.yaml"
