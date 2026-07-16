"""
app/api/sessions.py

Exposes saved session files from ~/.intentos/sessions/.
"""
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["Sessions"])

SESSIONS_DIR = Path.home() / ".intentos" / "sessions"


@router.get("")
async def list_sessions():
    """Return a list of all saved session metadata."""
    if not SESSIONS_DIR.exists():
        return {"sessions": []}
    
    sessions = []
    for path in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "job_id": data.get("job_id"),
                "goal": data.get("goal"),
                "status": data.get("status"),
                "stage": data.get("stage"),
                "step": data.get("step"),
                "max_steps": data.get("max_steps"),
                "created_at": data.get("created_at"),
                "error": data.get("error"),
            })
        except Exception:
            continue
    return {"sessions": sessions}


@router.get("/{job_id}")
async def get_session(job_id: str):
    """Return the full session data for a specific job."""
    path = SESSIONS_DIR / f"{job_id}.json"
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Session {job_id!r} not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
