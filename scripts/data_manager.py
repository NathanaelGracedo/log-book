# scripts/data_manager.py
import os
from pathlib import Path
import datetime
from typing import Optional, List, Tuple, Any
import yaml
from scripts.calendar_utils import (
    get_yaml_filename_for_date,
    get_month_bundles,
    get_month_bundle_weeks,
    get_internship_calendar,
    format_indonesian_date,
    INDONESIAN_DAYS
)

MONTH_FILE_TEMPLATES = [
    (7, 2026, "bulan_01_juli.yaml"),
    (8, 2026, "bulan_02_agustus.yaml"),
    (9, 2026, "bulan_03_september.yaml"),
    (10, 2026, "bulan_04_oktober.yaml"),
    (11, 2026, "bulan_05_november.yaml"),
    (12, 2026, "bulan_06_desember.yaml"),
]

def get_month_templates(config: Optional[dict] = None) -> List[Tuple[int, int, str]]:
    """Returns a list of (month, year, yaml_filename) tuples based on active calendar config."""
    bundles = get_month_bundles(config)
    if bundles:
        return [(b["month"], b["year"], b["yaml_filename"]) for b in bundles]
    return MONTH_FILE_TEMPLATES

def init_data_files(data_dir: str = "data", config: Optional[dict] = None) -> None:
    """Ensures that all monthly YAML data files exist with their skeleton headers."""
    target_path = Path(data_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    templates = get_month_templates(config)

    for bulan, tahun, filename in templates:
        file_path = target_path / filename
        if not file_path.exists():
            content = {
                "bulan": bulan,
                "tahun": tahun,
                "catatan": {}
            }
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, allow_unicode=True, default_flow_style=False)

def load_all_notes(data_dir: str = "data", config: Optional[dict] = None) -> dict:
    """Loads and merges all daily activity records from all monthly yaml files."""
    init_data_files(data_dir, config)
    target_path = Path(data_dir)
    merged_notes = {}
    templates = get_month_templates(config)

    for _, _, filename in templates:
        file_path = target_path / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                catatan = data.get("catatan") or {}
                for k, v in catatan.items():
                    if v is not None:
                        k_str = k.strftime("%Y-%m-%d") if isinstance(k, (datetime.date, datetime.datetime)) else str(k)
                        if isinstance(v, dict):
                            merged_notes[k_str] = {
                                "status": str(v.get("status", "hadir")).strip().lower(),
                                "kegiatan": str(v.get("kegiatan", "")).strip()
                            }
                        elif str(v).strip():
                            merged_notes[k_str] = str(v).strip()

    return merged_notes

def save_note_to_month(date_val: datetime.date, note: Any, data_dir: str = "data", config: Optional[dict] = None) -> None:
    """Saves or updates a daily note in the appropriate monthly YAML file."""
    filename = get_yaml_filename_for_date(date_val, config)
    target_path = Path(data_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    file_path = target_path / filename

    data = {}
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    if "bulan" not in data:
        data["bulan"] = date_val.month
    if "tahun" not in data:
        data["tahun"] = date_val.year
    if "catatan" not in data or not isinstance(data["catatan"], dict):
        data["catatan"] = {}

    catatan = data.get("catatan") or {}
    normalized_catatan = {}
    for k, v in catatan.items():
        k_str = k.strftime("%Y-%m-%d") if isinstance(k, (datetime.date, datetime.datetime)) else str(k)
        normalized_catatan[k_str] = v

    date_str = date_val.strftime("%Y-%m-%d")
    if isinstance(note, str):
        normalized_catatan[date_str] = note.strip()
    elif isinstance(note, dict):
        normalized_catatan[date_str] = {
            "status": str(note.get("status", "hadir")).strip().lower(),
            "kegiatan": str(note.get("kegiatan", "")).strip()
        }
    else:
        normalized_catatan[date_str] = note
    data["catatan"] = normalized_catatan

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def check_missing_dates(
    month_bundle_idx: int | None = None,
    data_dir: str = "data",
    config: Optional[dict] = None
) -> list[datetime.date]:
    """
    Finds missing dates with no note recorded.
    If month_bundle_idx (1..6 or dynamic) is provided, checks only weeks belonging to that bundle.
    If None, checks all calendar weeks.
    """
    if month_bundle_idx is not None:
        weeks = get_month_bundle_weeks(month_bundle_idx, config)
    else:
        weeks = get_internship_calendar(config)

    existing_notes = load_all_notes(data_dir, config)
    missing = []

    for w in weeks:
        for day in w["days"]:
            d_str = day["date_str"]
            if d_str not in existing_notes:
                missing.append(day["date"])

    return missing

def prompt_fill_missing(
    missing_dates: list[datetime.date],
    input_func=input,
    print_func=print,
    data_dir: str = "data",
    config: Optional[dict] = None
) -> int:
    """Interactively prompts the user in the CLI to fill missing activity entries."""
    if not missing_dates:
        return 0

    print_func(f"\n[INFO] Ditemukan {len(missing_dates)} hari kerja aktif yang belum memiliki catatan kegiatan.")
    print_func("Ketik catatan kegiatan, tekan [Enter] untuk lewati, atau ketik 'q' untuk keluar pengisian.\n")

    filled_count = 0
    for d in missing_dates:
        hari_name = INDONESIAN_DAYS[d.weekday()]
        d_fmt = format_indonesian_date(d)
        prompt_text = f"[{d.strftime('%Y-%m-%d')} - {hari_name}, {d_fmt}] Kegiatan: "

        try:
            val = input_func(prompt_text)
        except (KeyboardInterrupt, EOFError):
            print_func("\nPengisian dibatalkan oleh pengguna.")
            break

        if val is None:
            break
        val = val.strip()
        if val.lower() == "q":
            print_func("Keluar dari pengisian interaktif.")
            break
        if val:
            save_note_to_month(d, val, data_dir, config)
            filled_count += 1
            print_func(f"  -> Tersimpan untuk {d.strftime('%Y-%m-%d')}.")

    return filled_count
