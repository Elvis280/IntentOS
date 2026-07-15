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

The agent loop itself (_run_job) is a lightly refactored copy of the
original /run handler.  The only structural additions are:
  1. job.wait_if_paused()   — after each phase, yields if paused
  2. job.should_stop()      — checked at the top of every iteration
  3. job.update(...)        — records live state after each phase
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
from app.core.job_manager import job_manager, Job, JobStatus


router = APIRouter(prefix="/agent", tags=["Agent"])

capture  = ScreenCapture()
executor = Executor()


# ── Helpers ──────────────────────────────────────────────────────────────────

def fuzzy_duplicate(a: dict, b: dict) -> bool:
    """Return True if two actions are considered equivalent.

    For CLICK actions, coordinates within ±15 px on both axes are treated
    as the same action — catches retry loops where the reasoner varies
    coordinates slightly but repeats the same failed strategy.
    """
    if a["action"] != b["action"]:
        return False
    if a["action"] == "CLICK":
        ap = a.get("parameters", {})
        bp = b.get("parameters", {})
        return (
            abs(ap.get("x", 0) - bp.get("x", 0)) <= 15
            and abs(ap.get("y", 0) - bp.get("y", 0)) <= 15
        )
    return a.get("parameters") == b.get("parameters")


# ── The agent loop (runs in a background thread) ──────────────────────────────

def _run_job(job: Job) -> None:
    """
    Executes the full Observe→Reason→Policy→Execute→Verify loop for a job.
    Reads job.should_stop() and job.wait_if_paused() at every phase boundary
    so that pause/resume/stop work without killing the thread forcibly.
    """
    job.status = JobStatus.RUNNING
    history: list = []

    try:
        for step in range(1, job.max_steps + 1):

            # ── Stop check ───────────────────────────────────────────────────
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Pause gate ───────────────────────────────────────────────────
            job.wait_if_paused()
            if job.should_stop():          # may have been stopped while paused
                job.status = JobStatus.STOPPED
                return

            # ── Phase 1: Observe ─────────────────────────────────────────────
            job.update(stage="Observing", step=step)
            image  = capture.capture()
            vision = analyze(image)
            state  = build_world(vision)
            world.update(state)
            before = world.get().model_dump()

            # Encode the screenshot for the frontend
            import base64, io
            from PIL import Image as PILImage
            buf = io.BytesIO()
            # capture() returns a PIL Image; save as PNG into buffer
            img_obj = image if hasattr(image, "save") else PILImage.fromarray(image)
            img_obj.save(buf, format="PNG")
            screenshot_b64 = base64.b64encode(buf.getvalue()).decode()

            job.update(
                stage="Observing",
                world=before,
                screenshot=screenshot_b64,
                history=history,
            )

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 2: Reason ───────────────────────────────────────────────
            job.update(stage="Reasoning")
            action = next_action(job.goal, before, history, image)

            job.update(
                stage="Reasoning",
                thought=action.get("thought", ""),
                action=action,
            )

            # Repeated-action guard
            if history and fuzzy_duplicate(action, history[-1]["action"]):
                print("[Agent] Repeated action detected — stopping loop.")
                job.update(stage="Completed", thought="Repeated action detected. Stopping.")
                job.status = JobStatus.COMPLETED
                return

            if action["action"] == "DONE":
                job.update(stage="Completed", thought=action.get("thought", "Goal completed."))
                job.status = JobStatus.COMPLETED
                return

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 3: Policy ───────────────────────────────────────────────
            job.update(stage="Policy")
            action = policy.apply(
                goal=job.goal,
                world=before,
                history=history,
                action=action,
            )
            job.update(action=action)

            if action["action"] == "REASON_AGAIN":
                print("[Agent] Policy returned REASON_AGAIN — skipping execution.")
                history.append({"action": action, "verified": False})
                job.update(history=history)
                continue

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 4: Execute ──────────────────────────────────────────────
            job.update(stage="Executing")
            executor.execute(action)
            time.sleep(1.5)

            job.wait_if_paused()
            if job.should_stop():
                job.status = JobStatus.STOPPED
                return

            # ── Phase 5: Verify ───────────────────────────────────────────────
            job.update(stage="Verifying")
            image  = capture.capture()
            vision = analyze(image)
            state  = build_world(vision)
            world.update(state)
            after = world.get().model_dump()

            verified = verifier.verify(before, after, action)
            history.append({"action": action, "verified": verified})

            # Refresh screenshot after execution
            buf2 = io.BytesIO()
            img_obj2 = image if hasattr(image, "save") else PILImage.fromarray(image)
            img_obj2.save(buf2, format="PNG")
            screenshot_b64_after = base64.b64encode(buf2.getvalue()).decode()

            job.update(
                stage="Verifying",
                world=after,
                history=history,
                screenshot=screenshot_b64_after,
            )

            if not verified:
                print("[Agent] Verification failed.")
                job.update(stage="Failed", thought="Verification failed. Stopping.")
                job.status = JobStatus.FAILED
                return

        # Exhausted max_steps
        job.status = JobStatus.COMPLETED

    except Exception as exc:
        job.error  = str(exc)
        job.status = JobStatus.FAILED
        print(f"[Agent] Job {job.job_id} failed with exception: {exc}")


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
        target=_run_job,
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
            print("[Agent] Repeated action detected — stopping loop.")
            break

        print("=" * 50)
        print(action)
        print("=" * 50)

        if action["action"] == "DONE":
            break

        action = policy.apply(
            goal=data.goal,
            world=before,
            history=history,
            action=action,
        )

        if action["action"] == "REASON_AGAIN":
            print("[Agent] Policy returned REASON_AGAIN — skipping execution.")
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
            print("Verification failed.")
            break

    return {"goal": data.goal, "history": history}