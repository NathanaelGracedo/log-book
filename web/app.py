# web/app.py
"""
FastAPI Backend Application for Polinema Log Book Automation Dashboard.
Provides REST API endpoints for calendar monitoring, daily note CRUD,
narrative formalization, batch auto-filling, profile configuration,
and live PDF preview streaming.
"""

import os
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
from main import load_config

app = FastAPI(title="Log Book Polinema Dashboard API", version="1.0.0")

# Request Schemas
class SaveDayRequest(BaseModel):
    date: str
    note: str

class FormalizeRequest(BaseModel):
    note: str

class BatchAutofillRequest(BaseModel):
    overwrite_existing: bool = False

# Ensure data directory is initialized
init_data_files("data")

@app.get("/api/calendar")
def get_calendar() -> Dict[str, Any]:
    """Returns the full 27-week internship calendar, partitioned into 6 monthly bundles."""
    notes_map = load_all_notes("data")
    all_weeks = get_internship_calendar()
    
    total_days = sum(len(w["days"]) for w in all_weeks)
    filled_days = 0
    
    # Enrich day dicts with note and is_filled status
    enriched_calendar = []
    for w in all_weeks:
        week_days = []
        for d in w["days"]:
            d_str = d["date_str"]
            note = notes_map.get(d_str, "")
            is_filled = bool(note and note.strip())
            if is_filled:
                filled_days += 1
            day_copy = dict(d)
            day_copy["note"] = note
            day_copy["is_filled"] = is_filled
            day_copy["date"] = d["date"].strftime("%Y-%m-%d")
            week_days.append(day_copy)
        enriched_calendar.append({
            "minggu_ke": w["minggu_ke"],
            "days": week_days
        })
        
    missing_days = total_days - filled_days
    percentage = round((filled_days / total_days * 100), 1) if total_days > 0 else 0.0
    
    # Group into 6 monthly bundles
    months_data = []
    month_week_ranges = {
        1: (1, 5, "Juli 2026"),
        2: (6, 9, "Agustus 2026"),
        3: (10, 14, "September 2026"),
        4: (15, 18, "Oktober 2026"),
        5: (19, 22, "November 2026"),
        6: (23, 27, "Desember 2026"),
    }
    
    for m_idx, (w_start, w_end, name) in month_week_ranges.items():
        bundle_weeks = [w for w in enriched_calendar if w_start <= w["minggu_ke"] <= w_end]
        b_total = sum(len(w["days"]) for w in bundle_weeks)
        b_filled = sum(1 for w in bundle_weeks for d in w["days"] if d["is_filled"])
        months_data.append({
            "month_index": m_idx,
            "name": name,
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
        
    try:
        save_note_to_month(date_obj, payload.note, "data")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "date": payload.date, "note": payload.note}

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
    try:
        with open("config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(payload, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return {"status": "ok", "message": "Konfigurasi profil berhasil diperbarui."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
