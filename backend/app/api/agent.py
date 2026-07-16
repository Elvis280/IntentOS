"""
app/api/agent.py  (v2 — job-based architecture)

What changed vs v1
------------------
- POST /agent/run  →  kept for backward compatibility (synchronous, unchanged)
- POST /agent/start  →  new; kicks off the agent loop in a background thread
                         and immediately returns {"job_id": "..."}
- GET  /agent/status/{job_id}  →  returns full live state (polled by frontend)
- GET  /agent/history/{job_id} →  returns the execution history list only
- POST /agent/pause/{job_id}   →  pauses the running loop after current phase
- POST /agent/resume/{job_id}  →  unpauses
- POST /agent/stop/{job_id}    →  terminates the loop cleanly

"""

import time
import threading

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.verifier import verifier
from app.world.manager import world
from app.vision.capture import ScreenCapture
from app.vision.llm import analyze
from app.vision.analyzer import build_world
from app.executor.executor import Executor
from app.services.reasoner import next_action
from app.services.policy import policy
from app.runtime.job_manager import job_manager, JobStatus
from app.runtime.loop import run_job, fuzzy_duplicate
from app.core.logger import logger

router = APIRouter(prefix="/agent", tags=["Agent"])

capture  = ScreenCapture()
executor = Executor()


# ── Request models ────────────────────────────────────────────────────────────

class Goal(BaseModel):
    goal: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/start")
async def start_agent(data: Goal):
    """
    Create a new job and start the agent loop in a background thread.
    Returns immediately with the job_id for the frontend to poll.
    """
    job = job_manager.create(goal=data.goal)
    thread = threading.Thread(
        target=run_job,
        args=(job,),
        daemon=True,
        name=f"agent-job-{job.job_id[:8]}",
    )
    thread.start()
    return {"job_id": job.job_id}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Polled by the frontend every 500 ms.
    Returns the full live state of the job.
    """
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    return job.to_dict()


@router.get("/history/{job_id}")
async def get_history(job_id: str):
    """Returns only the execution history list for a job."""
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    return {"job_id": job_id, "history": job.history}


@router.post("/pause/{job_id}")
async def pause_agent(job_id: str):
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    if job.status != JobStatus.RUNNING:
        raise HTTPException(status_code=400, detail=f"Job is {job.status.value}, not running.")
    job.pause()
    return {"job_id": job_id, "status": job.status.value}


@router.post("/resume/{job_id}")
async def resume_agent(job_id: str):
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    if job.status != JobStatus.PAUSED:
        raise HTTPException(status_code=400, detail=f"Job is {job.status.value}, not paused.")
    job.resume()
    return {"job_id": job_id, "status": job.status.value}

class ClarificationResponse(BaseModel):
    answer: str

@router.post("/{job_id}/clarify")
async def clarify_agent(job_id: str, data: ClarificationResponse):
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    
    # Store the answer on the job
    job.clarification_answer = data.answer
    
    # Auto-resume the job if it was paused
    if job.status == JobStatus.PAUSED:
        job.resume()
        
    return {"job_id": job_id, "status": job.status.value}


@router.post("/stop/{job_id}")
async def stop_agent(job_id: str):
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id!r} not found.")
    job.stop()
    # Give the thread a brief moment to set its own status
    time.sleep(0.1)
    return {"job_id": job_id, "status": job.status.value}


# ── Legacy endpoint — unchanged, kept for backward compatibility ──────────────

@router.post("/run")
async def run_agent(data: Goal):
    """
    Original synchronous endpoint.
    Kept intact so any existing integrations continue to work.
    """
    history = []
    MAX_STEPS = 20

    for _ in range(MAX_STEPS):
        image  = capture.capture()
        vision = analyze(image)
        state  = build_world(vision)
        world.update(state)
        before = world.get().model_dump()

        action = next_action(data.goal, before, history, image)

        if history and fuzzy_duplicate(action, history[-1]["action"]):
            logger.warning("[Agent] Repeated action detected — stopping loop.")
            break

        logger.info("=" * 50)
        logger.info(action)
        logger.info("=" * 50)

        if action["action"] == "DONE":
            break

        action = policy.apply(
            goal=data.goal,
            world=before,
            history=history,
            action=action,
        )

        if action["action"] == "REASON_AGAIN":
            logger.warning("[Agent] Policy returned REASON_AGAIN — skipping execution.")
            history.append({"action": action, "verified": False})
            continue

        executor.execute(action)
        time.sleep(1.5)

        image  = capture.capture()
        vision = analyze(image)
        state  = build_world(vision)
        world.update(state)
        after = world.get().model_dump()

        verified = verifier.verify(before, after, action)
        history.append({"action": action, "verified": verified})

        if not verified:
            logger.warning("Verification failed.")
            break

    return {"goal": data.goal, "history": history}