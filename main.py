# main.py
"""
Log Book Polinema Automation CLI Orchestrator.

Coordinates asset extraction, calendar partitioning, YAML data management,
narrative expansion, and XeLaTeX PDF compilation.
"""

import argparse
import os
import sys
import yaml
from scripts.extract_assets import extract_assets_from_docx
from scripts.calendar_utils import (
    get_internship_calendar,
    get_month_bundle_weeks,
)
from scripts.data_manager import (
    init_data_files,
    load_all_notes,
    check_missing_dates,
    prompt_fill_missing,
)
from scripts.latex_builder import generate_latex_document, compile_pdf

OUTPUT_MONTHLY_FILENAMES = {
    1: "Logbook_01_Juli_2026.pdf",
    2: "Logbook_02_Agustus_2026.pdf",
    3: "Logbook_03_September_2026.pdf",
    4: "Logbook_04_Oktober_2026.pdf",
    5: "Logbook_05_November_2026.pdf",
    6: "Logbook_06_Desember_2026.pdf",
}
CUMULATIVE_FILENAME = "Logbook_Lengkap_Juli_Desember_2026.pdf"


def load_config(config_path: str = "config.yaml") -> dict:
    """Loads configuration YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Konfigurasi {config_path} tidak ditemukan.")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_assets():
    """Extracts required institutional logos if they are missing."""
    assets_dir = "assets"
    polinema_png = os.path.join(assets_dir, "polinema.png")
    kemendikbud_jpg = os.path.join(assets_dir, "kemendikbud.jpg")
    if (not os.path.exists(polinema_png) or not os.path.exists(kemendikbud_jpg)) and os.path.exists("Log Book Template.docx"):
        print("[INFO] Mengekstrak logo dari 'Log Book Template.docx'...")
        extract_assets_from_docx("Log Book Template.docx", assets_dir)


def build_pdf_bundle(weeks: list[dict], notes_map: dict[str, str], config: dict, out_name: str) -> str:
    """Builds a single PDF bundle for a collection of weeks."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out_pdf = os.path.join(output_dir, out_name)
    print(f"[BUILD] Men-generate {out_name} ({len(weeks)} halaman)...")
    latex_doc = generate_latex_document(weeks, notes_map, config)
    compile_pdf(latex_doc, out_pdf)
    print(f"[OK] Berhasil: {out_pdf}")
    return out_pdf


def main():
    parser = argparse.ArgumentParser(description="Log Book Polinema Automation Generator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--month", type=int, choices=range(1, 7), help="Pilih bulan ke-1 s/d 6 untuk digenerate")
    group.add_argument("--all", action="store_true", help="Generate semua 6 bulan + 1 file kumulatif")
    group.add_argument("--cumulative-only", action="store_true", help="Hanya generate file PDF kumulatif")
    parser.add_argument("--check-only", action="store_true", help="Hanya cek tanggal kosong tanpa kompilasi PDF")
    parser.add_argument("--non-interactive", action="store_true", help="Nonaktifkan prompt interaktif untuk tanggal kosong")
    parser.add_argument("--ui", action="store_true", help="Jalankan antarmuka web dashboard interaktif")
    parser.add_argument("--port", type=int, default=8000, help="Port server web UI (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host server web UI (default: 127.0.0.1)")
    args = parser.parse_args()

    if args.ui:
        import uvicorn
        ensure_assets()
        init_data_files("data")
        print(f"\n========================================================")
        print(f"🚀 Log Book Polinema Web Dashboard Berjalan!")
        print(f"📍 Akses di peramban web: http://{args.host}:{args.port}")
        print(f"========================================================\n")
        uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
        sys.exit(0)

    ensure_assets()
    init_data_files("data")
    config = load_config("config.yaml")

    # Determine which target bundles to process
    if args.month:
        target_months = [args.month]
    elif args.cumulative_only:
        target_months = []
    else:
        target_months = list(range(1, 7))

    # Check missing dates
    if args.cumulative_only or args.all or (not args.month):
        missing = check_missing_dates(None, "data")
    else:
        missing = check_missing_dates(args.month, "data")

    if missing:
        if args.non_interactive:
            print(f"[PERINGATAN] Ditemukan {len(missing)} tanggal aktif yang belum memiliki catatan kegiatan.")
        else:
            prompt_fill_missing(missing, data_dir="data")

    if args.check_only:
        print("[INFO] Pemeriksaan tanggal selesai.")
        sys.exit(0)

    # Reload notes after possible interactive fills
    notes_map = load_all_notes("data")

    generated = []

    # Build targeted monthly PDFs
    if not args.cumulative_only:
        for m_idx in target_months:
            weeks = get_month_bundle_weeks(m_idx)
            out_name = OUTPUT_MONTHLY_FILENAMES[m_idx]
            pdf_path = build_pdf_bundle(weeks, notes_map, config, out_name)
            generated.append(pdf_path)

    # Build cumulative PDF if requested
    if args.all or args.cumulative_only:
        all_weeks = get_internship_calendar()
        pdf_path = build_pdf_bundle(all_weeks, notes_map, config, CUMULATIVE_FILENAME)
        generated.append(pdf_path)

    print("\n[SELESAI] Ringkasan berkas PDF yang dihasilkan:")
    for path in generated:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
