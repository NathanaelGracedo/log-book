# scripts/calendar_utils.py
import datetime
from typing import Optional, List, Dict, Tuple
from collections import Counter

INDONESIAN_DAYS: dict[int, str] = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

INDONESIAN_MONTHS: dict[int, str] = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

# Legacy mapping of month report index (1..6) to (start_week, end_week)
MONTH_BUNDLE_WEEKS: dict[int, tuple[int, int]] = {
    1: (1, 5),    # Juli
    2: (6, 9),    # Agustus
    3: (10, 14),  # September
    4: (15, 18),  # Oktober
    5: (19, 22),  # November
    6: (23, 27),  # Desember
}

DEFAULT_START_DATE = datetime.date(2026, 7, 1)
DEFAULT_END_DATE = datetime.date(2026, 12, 31)
START_DATE = DEFAULT_START_DATE
END_DATE = DEFAULT_END_DATE

def format_indonesian_date(d: datetime.date) -> str:
    """Returns date in format: 1 Juli 2026"""
    month_name = INDONESIAN_MONTHS.get(d.month, str(d.month))
    return f"{d.day} {month_name} {d.year}"

def parse_config_period(config: Optional[dict] = None) -> Tuple[datetime.date, datetime.date, str]:
    """Extracts start date, end date, and work days mode from config dictionary."""
    if not config:
        return DEFAULT_START_DATE, DEFAULT_END_DATE, "senin_sabtu"

    periode = (config.get("periode") or {})
    start_str = periode.get("tanggal_mulai")
    end_str = periode.get("tanggal_selesai")

    start_d = datetime.date.fromisoformat(str(start_str)) if start_str else DEFAULT_START_DATE
    end_d = datetime.date.fromisoformat(str(end_str)) if end_str else DEFAULT_END_DATE

    hari_kerja = (config.get("pengaturan") or {}).get("hari_kerja", "senin_sabtu")
    if hari_kerja not in ("senin_jumat", "senin_sabtu"):
        hari_kerja = "senin_sabtu"

    return start_d, end_d, hari_kerja

def get_calendar_working_days(month_num: Optional[int] = None, config: Optional[dict] = None) -> List[datetime.date]:
    """Returns all active working days within the internship period or for a specific month."""
    start_d, end_d, work_days_mode = parse_config_period(config)
    curr = start_d
    days = []
    while curr <= end_d:
        w_day = curr.weekday()
        is_active = (work_days_mode == "senin_jumat" and w_day in range(0, 5)) or \
                    (work_days_mode == "senin_sabtu" and w_day in range(0, 6))
        if is_active:
            if month_num is None or curr.month == month_num:
                days.append(curr)
        curr += datetime.timedelta(days=1)
    return days

def get_internship_calendar(
    config: Optional[dict] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    work_days: Optional[str] = None
) -> List[dict]:
    """
    Partitions the internship period into sequential weeks.
    Respects custom range, 5-day (senin_jumat) or 6-day (senin_sabtu) schedule,
    and custom working hours from config.
    """
    cfg_start, cfg_end, cfg_work = parse_config_period(config)
    start_d = start_date or cfg_start
    end_d = end_date or cfg_end
    work_days_mode = work_days or cfg_work

    weeks = []
    current_days = []
    curr = start_d
    week_num = 1

    jam_senin_jumat_masuk = "08.00"
    jam_senin_jumat_pulang = "16.00"
    jam_sabtu_pulang = "14.00"
    if config:
        jam_cfg = (config.get("pengaturan") or {}).get("jam_kerja") or {}
        sj = jam_cfg.get("senin_jumat") or {}
        sabtu = jam_cfg.get("sabtu") or {}
        jam_senin_jumat_masuk = sj.get("masuk") or "08.00"
        jam_senin_jumat_pulang = sj.get("pulang") or "16.00"
        jam_sabtu_pulang = sabtu.get("pulang") or "14.00"

    while curr <= end_d:
        w_day = curr.weekday()
        is_active = False

        if work_days_mode == "senin_jumat" and w_day in range(0, 5):  # Mon-Fri
            is_active = True
            jam_masuk = jam_senin_jumat_masuk
            jam_pulang = jam_senin_jumat_pulang
        elif work_days_mode == "senin_sabtu" and w_day in range(0, 6):  # Mon-Sat
            is_active = True
            jam_masuk = jam_senin_jumat_masuk
            jam_pulang = jam_sabtu_pulang if w_day == 5 else jam_senin_jumat_pulang

        if is_active:
            current_days.append({
                "date": curr,
                "date_str": curr.strftime("%Y-%m-%d"),
                "hari": INDONESIAN_DAYS[w_day],
                "tanggal_str": format_indonesian_date(curr),
                "jam_masuk": jam_masuk,
                "jam_pulang": jam_pulang,
            })

        end_of_week = (work_days_mode == "senin_jumat" and w_day == 4) or \
                      (work_days_mode == "senin_sabtu" and w_day == 5) or \
                      (curr == end_d)

        if end_of_week:
            if current_days:
                weeks.append({
                    "minggu_ke": week_num,
                    "days": current_days
                })
                week_num += 1
                current_days = []

        curr += datetime.timedelta(days=1)

    return weeks

def get_month_bundles(config: Optional[dict] = None) -> List[dict]:
    """
    Groups weeks from get_internship_calendar into monthly bundles
    based on the dominant calendar month of each week.
    """
    all_weeks = get_internship_calendar(config)
    if not all_weeks:
        return []

    # Identify dominant (year, month) for each week
    month_week_map: dict[tuple[int, int], list[dict]] = {}
    for w in all_weeks:
        months_in_week = [d["date"].month for d in w["days"]]
        dominant_month = Counter(months_in_week).most_common(1)[0][0]
        dominant_year = None
        for d in w["days"]:
            if d["date"].month == dominant_month:
                dominant_year = d["date"].year
                break
        key = (dominant_year, dominant_month)
        month_week_map.setdefault(key, []).append(w)

    bundles = []
    bundle_idx = 1
    sorted_keys = sorted(month_week_map.keys())
    for yr, mo in sorted_keys:
        weeks_in_bundle = month_week_map[(yr, mo)]
        month_name = INDONESIAN_MONTHS.get(mo, str(mo))
        w_start = weeks_in_bundle[0]["minggu_ke"]
        w_end = weeks_in_bundle[-1]["minggu_ke"]
        bundles.append({
            "bundle_index": bundle_idx,
            "month": mo,
            "year": yr,
            "month_name": month_name,
            "name": f"{month_name} {yr}",
            "filename": f"Logbook_{bundle_idx:02d}_{month_name}_{yr}.pdf",
            "yaml_filename": f"bulan_{bundle_idx:02d}_{month_name.lower()}.yaml",
            "start_week": w_start,
            "end_week": w_end,
            "weeks": weeks_in_bundle
        })
        bundle_idx += 1

    return bundles

def get_month_bundle_weeks(bundle_index: int, config: Optional[dict] = None) -> List[dict]:
    """Returns the list of weeks belonging to a specific monthly report bundle."""
    bundles = get_month_bundles(config)
    for b in bundles:
        if b["bundle_index"] == bundle_index:
            return b["weeks"]
    raise ValueError(f"Bundle index {bundle_index} tidak ditemukan dalam periode kalender.")

def get_yaml_filename_for_date(d: datetime.date, config: Optional[dict] = None) -> str:
    """Maps a given date to its corresponding YAML filename."""
    start_d, end_d, _ = parse_config_period(config)
    if d < start_d or d > end_d:
        raise ValueError(f"Date {d} is outside the internship period ({start_d} to {end_d})")

    bundles = get_month_bundles(config)
    for b in bundles:
        if b["month"] == d.month and b["year"] == d.year:
            return b["yaml_filename"]

    for b in bundles:
        for w in b["weeks"]:
            for day in w["days"]:
                if day["date"] == d:
                    return b["yaml_filename"]

    # Fallback by calendar month
    mo_name = INDONESIAN_MONTHS.get(d.month, "bulan").lower()
    return f"bulan_{d.month:02d}_{mo_name}.yaml"
