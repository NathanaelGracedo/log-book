# web/app.py
"""
FastAPI Backend Application for Polinema Log Book Automation Dashboard.
Provides REST API endpoints for calendar monitoring, daily note CRUD,
narrative formalization, batch auto-filling, profile configuration,
and live PDF preview streaming.
"""

import os
import tempfile
import datetime
from pathlib import Path
from typing import Optional, Any, Dict
import yaml
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from scripts.calendar_utils import (
    get_internship_calendar,
    get_month_bundle_weeks,
    get_month_bundles,
    INDONESIAN_MONTHS,
    format_indonesian_date
)
from scripts.data_manager import (
    load_all_notes,
    save_note_to_month,
    init_data_files
)
from scripts.narrative_expander import expand_narrative
from scripts.curriculum import batch_autofill_notes
from main import (
    load_config,
    build_pdf_bundle,
    OUTPUT_MONTHLY_FILENAMES,
    CUMULATIVE_FILENAME,
    ensure_assets
)

app = FastAPI(title="Log Book Polinema Dashboard API", version="1.0.0")

# Request Schemas
class SaveDayRequest(BaseModel):
    date: str
    note: str
    status: str = "hadir"

class FormalizeRequest(BaseModel):
    note: str

class BatchAutofillRequest(BaseModel):
    overwrite_existing: bool = False

class GeneratePdfRequest(BaseModel):
    target: Any # 1..6 or "cumulative" or "all"

# Ensure data directory and configuration are initialized
config = load_config("config.yaml")
init_data_files("data", config)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html tidak ditemukan")
    return FileResponse(index_path, media_type="text/html")

@app.get("/api/calendar")
def get_calendar() -> Dict[str, Any]:
    """Returns the internship calendar partitioned into monthly bundles based on config."""
    config = load_config("config.yaml")
    notes_map = load_all_notes("data", config=config)
    all_weeks = get_internship_calendar(config=config)
    bundles = get_month_bundles(config=config)

    total_days = sum(len(w["days"]) for w in all_weeks)
    filled_days = 0

    # Enrich day dicts with note, kegiatan, attendance_status, and is_filled status
    enriched_calendar = []
    for w in all_weeks:
        week_days = []
        for d in w["days"]:
            d_str = d["date_str"]
            raw_entry = notes_map.get(d_str, "")
            if isinstance(raw_entry, dict):
                att_status = str(raw_entry.get("status", "hadir")).strip().lower() or "hadir"
                kegiatan = str(raw_entry.get("kegiatan", "")).strip()
            else:
                att_status = "hadir"
                kegiatan = str(raw_entry).strip() if raw_entry else ""

            is_filled = bool((att_status != "hadir") or (kegiatan and kegiatan.strip()))
            if is_filled:
                filled_days += 1

            day_copy = dict(d)
            day_copy["note"] = kegiatan
            day_copy["kegiatan"] = kegiatan
            day_copy["attendance_status"] = att_status
            day_copy["is_filled"] = is_filled
            day_copy["date"] = d["date"].strftime("%Y-%m-%d")
            week_days.append(day_copy)

        enriched_calendar.append({
            "minggu_ke": w["minggu_ke"],
            "days": week_days
        })

    missing_days = total_days - filled_days
    percentage = round((filled_days / total_days * 100), 1) if total_days > 0 else 0.0

    # Group into dynamic monthly bundles
    months_data = []
    enriched_by_week = {w["minggu_ke"]: w for w in enriched_calendar}

    for b in bundles:
        w_start = b["start_week"]
        w_end = b["end_week"]
        bundle_weeks = [enriched_by_week[w["minggu_ke"]] for w in b["weeks"] if w["minggu_ke"] in enriched_by_week]
        b_total = sum(len(w["days"]) for w in bundle_weeks)
        b_filled = sum(1 for w in bundle_weeks for d in w["days"] if d["is_filled"])
        months_data.append({
            "month_index": b["bundle_index"],
            "name": b["name"],
            "weeks_range": f"Minggu {w_start} - {w_end}",
            "total_count": b_total,
            "filled_count": b_filled,
            "missing_count": b_total - b_filled,
            "percentage": round((b_filled / b_total * 100), 1) if b_total > 0 else 0.0,
            "weeks": bundle_weeks
        })

    return {
        "total_days": total_days,
        "filled_days": filled_days,
        "missing_days": missing_days,
        "percentage": percentage,
        "months": months_data
    }

@app.post("/api/save-day")
def save_day(payload: SaveDayRequest):
    """Saves or updates an activity note for a specific date."""
    try:
        date_obj = datetime.datetime.strptime(payload.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal tidak valid. Gunakan YYYY-MM-DD.")

    status = (payload.status or "hadir").strip().lower()
    if status != "hadir":
        note_data = {"status": status, "kegiatan": payload.note}
    else:
        note_data = payload.note

    config = load_config("config.yaml")
    try:
        save_note_to_month(date_obj, note_data, "data", config=config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "ok",
        "date": payload.date,
        "note": payload.note,
        "attendance_status": status
    }

@app.post("/api/formalize")
def formalize_note(payload: FormalizeRequest):
    """Expands a brief activity bullet into a formal Indonesian sentence."""
    formalized = expand_narrative(payload.note)
    return {"status": "ok", "formalized": formalized}

@app.post("/api/batch-autofill")
def batch_autofill(payload: BatchAutofillRequest = Body(default=BatchAutofillRequest())):
    """Automatically fills missing dates with PT Naraya Telematika IT curriculum activities."""
    filled, empty = batch_autofill_notes(overwrite_existing=payload.overwrite_existing, data_dir="data")
    return {
        "status": "ok",
        "filled_count": filled,
        "message": f"Berhasil melengkapi {filled} tanggal kegiatan magang industri."
    }

@app.get("/api/config")
def get_config():
    """Reads current profile configuration from config.yaml."""
    return load_config("config.yaml")

@app.post("/api/config")
def update_config(payload: Dict[str, Any]):
    """Updates profile configuration in config.yaml."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=".", delete=False, encoding="utf-8") as f:
            temp_path = f.name
            yaml.dump(payload, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(temp_path, "config.yaml")
        temp_path = None
        return {"status": "ok", "message": "Konfigurasi profil berhasil diperbarui."}
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-pdf")
def generate_pdf(payload: GeneratePdfRequest):
    """Triggers XeLaTeX compilation for the requested target bundle."""
    ensure_assets()
    config = load_config("config.yaml")
    notes_map = load_all_notes("data", config=config)
    bundles = get_month_bundles(config)
    bundle_map = {b["bundle_index"]: b for b in bundles}

    if bundles:
        start_m = bundles[0]["month_name"]
        end_m = bundles[-1]["month_name"]
        end_yr = bundles[-1]["year"]
        cumulative_name = f"Logbook_Lengkap_{start_m}_{end_m}_{end_yr}.pdf" if start_m != end_m else f"Logbook_Lengkap_{start_m}_{end_yr}.pdf"
    else:
        cumulative_name = CUMULATIVE_FILENAME

    target = payload.target
    generated_urls = []

    if target == "all":
        # Compile all dynamic monthly bundles + 1 cumulative
        for b in bundles:
            weeks = b["weeks"]
            out_name = b["filename"]
            build_pdf_bundle(weeks, notes_map, config, out_name)
            generated_urls.append(f"/api/pdf/{out_name}")

        all_weeks = get_internship_calendar(config)
        build_pdf_bundle(all_weeks, notes_map, config, cumulative_name)
        generated_urls.append(f"/api/pdf/{cumulative_name}")

        return {
            "status": "ok",
            "target": "all",
            "pdf_url": generated_urls[0] if generated_urls else f"/api/pdf/{cumulative_name}",
            "all_urls": generated_urls,
            "message": f"Semua {len(bundles)} berkas PDF bulanan dan 1 berkas kumulatif berhasil dibuat."
        }

    elif target == "cumulative":
        all_weeks = get_internship_calendar(config)
        build_pdf_bundle(all_weeks, notes_map, config, cumulative_name)
        return {
            "status": "ok",
            "target": "cumulative",
            "pdf_url": f"/api/pdf/{cumulative_name}",
            "filename": cumulative_name
        }

    else:
        try:
            m_idx = int(target)
            if m_idx not in bundle_map:
                raise ValueError()
        except (ValueError, TypeError):
            max_idx = max(bundle_map.keys()) if bundle_map else 6
            raise HTTPException(status_code=400, detail=f"Target bulan harus berupa angka 1 s/d {max_idx}, 'cumulative', atau 'all'.")

        b = bundle_map[m_idx]
        weeks = b["weeks"]
        out_name = b["filename"]
        build_pdf_bundle(weeks, notes_map, config, out_name)
        return {
            "status": "ok",
            "target": m_idx,
            "pdf_url": f"/api/pdf/{out_name}",
            "filename": out_name
        }

@app.get("/api/pdf/{filename}")
def stream_pdf(filename: str):
    """Streams a generated PDF file from output/ directory inline for browser viewing."""
    # Prevent directory traversal
    clean_name = os.path.basename(filename)
    if clean_name != filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nama berkas tidak valid.")
        
    pdf_path = os.path.join("output", clean_name)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Berkas PDF belum digenerate. Silakan klik tombol 'Generate PDF' terlebih dahulu.")
        
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={clean_name}"}
    )

