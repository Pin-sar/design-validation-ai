import datetime as dt
import uuid
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.storage import storage
from app.pipeline.analyzer import analyze_samples
from app.pipeline.collector import run_emulator_and_collect

router = APIRouter()


class RunRequest(BaseModel):
    profile: Literal["baseline", "cache_stress", "timing_bug"] = "baseline"
    duration_sec: Optional[int] = Field(None, ge=5, le=300)
    hz: Optional[int] = Field(None, ge=1, le=200)


class RunResponse(BaseModel):
    run_id: str
    created_at: str
    profile: str
    samples: int
    parse_failures: int


@router.get("/health")
def health():
    return {
        "status": "ok",
        "db_path": settings.DB_PATH,
        "emu_default_duration_sec": settings.EMU_DURATION_SEC,
        "emu_default_hz": settings.EMU_LOG_HZ,
    }


@router.post("/runs", response_model=RunResponse)
def create_run(req: RunRequest):
    run_id = str(uuid.uuid4())
    created_at = dt.datetime.utcnow().isoformat() + "Z"

    duration = req.duration_sec or settings.EMU_DURATION_SEC
    hz = req.hz or settings.EMU_LOG_HZ

    cmd = [
        "python",
        "-m",
        "app.emu.mock_emulator",
        "--duration",
        str(duration),
        "--hz",
        str(hz),
        "--seed",
        str(settings.EMU_SEED),
        "--profile",
        req.profile,
    ]

    cr = run_emulator_and_collect(cmd)
    if cr.exit_code != 0:
        raise HTTPException(status_code=500, detail=f"Emulator failed with exit_code={cr.exit_code}")

    meta = {"profile": req.profile, "duration_sec": duration, "hz": hz, "seed": settings.EMU_SEED}
    storage.insert_run(run_id, created_at, meta)
    storage.insert_samples(run_id, cr.parsed_rows)

    return RunResponse(
        run_id=run_id,
        created_at=created_at,
        profile=req.profile,
        samples=len(cr.parsed_rows),
        parse_failures=cr.parse_failures,
    )


@router.get("/runs")
def list_runs():
    return storage.list_runs()


@router.get("/runs/{run_id}/report")
def run_report(run_id: str):
    samples = storage.get_samples(run_id)
    if not samples:
        raise HTTPException(status_code=404, detail="Run not found or has no samples")
    report = analyze_samples(samples)
    return {
        "run_id": run_id,
        "kpis": report.kpis,
        "bottlenecks": report.bottlenecks,
        "ml": report.ml,
    }
