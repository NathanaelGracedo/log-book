# main.py
"""
Log Book Polinema Automation CLI Orchestrator.

Coordinates asset extraction, calendar partitioning, YAML data management,
narrative expansion, and XeLaTeX PDF compilation.
"""

import argparse
import os
import shutil
import sys
import yaml
from scripts.extract_assets import extract_assets_from_docx
from scripts.calendar_utils import (
    get_internship_calendar,
    get_month_bundles,
    get_month_bundle_weeks,
)
from scripts.data_manager import (
    init_data_files,
    load_all_notes,
    check_missing_dates,
    prompt_fill_missing,
)
from scripts.latex_builder import generate_latex_document, compile_pdf
from scripts.doctor import run_doctor

OUTPUT_MONTHLY_FILENAMES = {
    1: "Logbook_01_Juli_2026.pdf",
    2: "Logbook_02_Agustus_2026.pdf",
    3: "Logbook_03_September_2026.pdf",
    4: "Logbook_04_Oktober_2026.pdf",
    5: "Logbook_05_November_2026.pdf",
    6: "Logbook_06_Desember_2026.pdf",
}
CUMULATIVE_FILENAME = "Logbook_Lengkap_Juli_Desember_2026.pdf"


def run_setup_wizard(config_path: str = "config.yaml") -> dict:
    print("\n========================================================")
    print("🪄 WIZARD KONFIGURASI LOG BOOK MAGANG POLINEMA")
    print("========================================================\n")

    nama = input("Nama Mahasiswa: ").strip() or "Nama Mahasiswa"
    nim = input("NIM: ").strip() or "XXXXXXXXXX"
    prodi = input("Program Studi [Sarjana Terapan Teknik Informatika]: ").strip() or "Sarjana Terapan Teknik Informatika"
    mitra = input("Nama Mitra Industri: ").strip() or "Mitra Industri"

    tgl_mulai = input("Tanggal Mulai Magang (YYYY-MM-DD) [2026-07-01]: ").strip() or "2026-07-01"
    tgl_selesai = input("Tanggal Selesai Magang (YYYY-MM-DD) [2026-12-31]: ").strip() or "2026-12-31"

    print("\nPilih Jadwal Kerja:")
    print("  1. 5 Hari Kerja (Senin - Jumat)")
    print("  2. 6 Hari Kerja (Senin - Sabtu)")
    jadwal_opt = input("Pilihan [2]: ").strip() or "2"
    hari_kerja = "senin_jumat" if jadwal_opt == "1" else "senin_sabtu"

    nama_dosen = input("\nNama Dosen Pembimbing: ").strip() or ""
    nip_dosen = input("NIP Dosen Pembimbing: ").strip() or ""
    nama_lapangan = input("Nama Pembimbing Lapangan (Mentor): ").strip() or ""
    nik_lapangan = input("NIK / ID Pembimbing Lapangan: ").strip() or ""

    config = {
        "mahasiswa": {"nama": nama, "nim": nim, "prodi": prodi, "mitra": mitra},
        "periode": {"tanggal_mulai": tgl_mulai, "tanggal_selesai": tgl_selesai},
        "pengaturan": {
            "hari_kerja": hari_kerja,
            "jam_kerja": {
                "senin_jumat": {"masuk": "08.00", "pulang": "16.00"},
                "sabtu": {"masuk": "08.00", "pulang": "14.00"}
            }
        },
        "pembimbing": {
            "dosen": {"nama": nama_dosen, "nip": nip_dosen},
            "lapangan": {"nama": nama_lapangan, "nik": nik_lapangan}
        }
    }

    dir_name = os.path.dirname(config_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n[OK] Konfigurasi berhasil disimpan ke '{config_path}'.\n")
    return config


def load_config(config_path: str = "config.yaml", example_path: str = "config.example.yaml") -> dict:
    """
    Loads configuration YAML file.
    If config_path is missing, automatically bootstraps it from example_path.
    """
    if not os.path.exists(config_path):
        should_bootstrap = (
            example_path is not None
            and (example_path != "config.example.yaml" or os.path.basename(config_path) in ("config.yaml", "config.yml"))
        )
        if should_bootstrap:
            if os.path.exists(example_path):
                print(f"[BOOTSTRAP] Berkas '{config_path}' tidak ditemukan. Menyalin template dari '{example_path}'...")
                shutil.copyfile(example_path, config_path)
                print(f"[BOOTSTRAP] Silakan sesuaikan data diri dan mitra pada '{config_path}' sesuai kebutuhan Anda.")
            else:
                raise FileNotFoundError(f"Konfigurasi '{config_path}' dan template '{example_path}' tidak ditemukan.")
        else:
            raise FileNotFoundError(f"Konfigurasi '{config_path}' tidak ditemukan.")

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
    parser.add_argument("--init", action="store_true", help="Jalankan wizard konfigurasi interaktif")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--month", type=int, help="Pilih bulan untuk digenerate")
    group.add_argument("--all", action="store_true", help="Generate semua bulan + 1 file kumulatif")
    group.add_argument("--cumulative-only", action="store_true", help="Hanya generate file PDF kumulatif")
    parser.add_argument("--check-only", action="store_true", help="Hanya cek tanggal kosong tanpa kompilasi PDF")
    parser.add_argument("--non-interactive", action="store_true", help="Nonaktifkan prompt interaktif untuk tanggal kosong")
    parser.add_argument("--ui", action="store_true", help="Jalankan antarmuka web dashboard interaktif")
    parser.add_argument("--port", type=int, default=8000, help="Port server web UI (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host server web UI (default: 127.0.0.1)")
    args = parser.parse_args()

    if args.init:
        run_setup_wizard("config.yaml")
        sys.exit(0)

    # Pre-flight check: UI or PDF compilation requires xelatex unless --check-only is given
    if not args.check_only:
        run_doctor(exit_on_failure=True)

    if args.ui:
        import uvicorn
        config = load_config("config.yaml")
        ensure_assets()
        init_data_files("data", config)
        print(f"\n========================================================")
        print(f"🚀 Log Book Polinema Web Dashboard Berjalan!")
        print(f"📍 Akses di peramban web: http://{args.host}:{args.port}")
        print(f"========================================================\n")
        uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
        sys.exit(0)

    config = load_config("config.yaml")
    ensure_assets()
    init_data_files("data", config=config)

    bundles = get_month_bundles(config)
    available_indices = [b["bundle_index"] for b in bundles]

    if args.month is not None and args.month not in available_indices:
        parser.error(f"argument -m/--month: invalid choice: {args.month} (pilihan yang tersedia: 1 s/d {len(available_indices)})")

    # Determine which target bundles to process
    if args.month:
        target_bundles = [b for b in bundles if b["bundle_index"] == args.month]
    elif args.cumulative_only:
        target_bundles = []
    else:
        target_bundles = bundles

    # Check missing dates
    if args.cumulative_only or args.all or (not args.month):
        missing = check_missing_dates(None, "data", config=config)
    else:
        missing = check_missing_dates(args.month, "data", config=config)

    if missing:
        if args.non_interactive:
            print(f"[PERINGATAN] Ditemukan {len(missing)} tanggal aktif yang belum memiliki catatan kegiatan.")
        else:
            prompt_fill_missing(missing, data_dir="data")

    if args.check_only:
        print("[INFO] Pemeriksaan tanggal selesai.")
        sys.exit(0)

    # Reload notes after possible interactive fills
    notes_map = load_all_notes("data", config=config)

    generated = []

    # Build targeted monthly PDFs
    if not args.cumulative_only:
        for bundle in target_bundles:
            weeks = bundle["weeks"]
            out_name = bundle["filename"]
            pdf_path = build_pdf_bundle(weeks, notes_map, config, out_name)
            generated.append(pdf_path)

    # Build cumulative PDF if requested
    if args.all or args.cumulative_only:
        all_weeks = get_internship_calendar(config)
        if bundles:
            start_m = bundles[0]["month_name"]
            end_m = bundles[-1]["month_name"]
            end_yr = bundles[-1]["year"]
            cumulative_name = f"Logbook_Lengkap_{start_m}_{end_m}_{end_yr}.pdf" if start_m != end_m else f"Logbook_Lengkap_{start_m}_{end_yr}.pdf"
        else:
            cumulative_name = CUMULATIVE_FILENAME
        pdf_path = build_pdf_bundle(all_weeks, notes_map, config, cumulative_name)
        generated.append(pdf_path)

    print("\n[SELESAI] Ringkasan berkas PDF yang dihasilkan:")
    for path in generated:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
