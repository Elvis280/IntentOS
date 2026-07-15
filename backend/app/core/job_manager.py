"""
app/core/job_manager.py

Lightweight in-memory Job Manager for IntentOS.

Each call to POST /agent/start creates a Job (UUID) that runs the agent
loop in a background thread.  The frontend polls GET /agent/status/{job_id}
every 500 ms to get live progress without WebSockets.

Lifecycle
---------
created  → running  → completed | failed
                     ↕
                   paused
                     ↕
                  (resume)
                     ↕
                  stopped   (terminal, like completed)

Pause/Resume mechanics
----------------------
The agent loop checks job.should_pause() after every phase.  When paused,
it sleeps in a tight loop until resumed or stopped.  This lets the frontend
freeze and unfreeze execution without killing the thread.
"""

import uuid
import time
import threading
import base64
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ── Status enum ──────────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    CREATED   = "created"
    RUNNING   = "running"
    PAUSED    = "paused"
    COMPLETED = "completed"
    FAILED    = "failed"
    STOPPED   = "stopped"


# ── Job ──────────────────────────────────────────────────────────────────────

class Job:
    """Represents one agent execution run."""

    def __init__(self, goal: str, max_steps: int = 20):
        self.job_id: str        = str(uuid.uuid4())
        self.goal: str          = goal
        self.max_steps: int     = max_steps
        self.created_at: str    = datetime.now(timezone.utc).isoformat()

        # Mutable state — written by the agent thread, read by API handlers
        self.status: JobStatus  = JobStatus.CREATED
        self.stage: str         = "idle"
        self.step: int          = 0
        self.progress: float    = 0.0
        self.thought: str       = ""
        self.action: dict       = {}
        self.world: dict        = {}
        self.history: list      = []
        self.screenshot: str    = ""   # base64 PNG
        self.error: str         = ""

        # Pause / stop signals (set from API handler, read by agent thread)
        self._pause_event  = threading.Event()   # set = running, clear = paused
        self._stop_event   = threading.Event()   # set = stop requested

        self._pause_event.set()   # starts in running state

    # ── Control API ──────────────────────────────────────────────────────────

    def pause(self):
        """Signal the agent loop to pause after the current phase."""
        if self.status == JobStatus.RUNNING:
            self._pause_event.clear()
            self.status = JobStatus.PAUSED

    def resume(self):
        """Unblock a paused agent loop."""
        if self.status == JobStatus.PAUSED:
            self.status = JobStatus.RUNNING
            self._pause_event.set()

    def stop(self):
        """Signal the agent loop to stop cleanly."""
        self._stop_event.set()
        self._pause_event.set()   # unblock if paused so the thread can exit

    # ── Checks called by the agent thread ────────────────────────────────────

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def wait_if_paused(self):
        """Block the agent thread while the job is paused."""
        self._pause_event.wait()

    # ── State update ─────────────────────────────────────────────────────────

    def update(
        self,
        *,
        stage: str       = None,
        thought: str     = None,
        action: dict     = None,
        world: dict      = None,
        history: list    = None,
        screenshot: str  = None,   # raw bytes or base64 string
        step: int        = None,
    ):
        """Called by the agent loop after each phase."""
        if stage      is not None: self.stage      = stage
        if thought    is not None: self.thought    = thought
        if action     is not None: self.action     = action
        if world      is not None: self.world      = world
        if history    is not None: self.history    = history
        if step       is not None:
            self.step     = step
            self.progress = round(step / self.max_steps, 4)

        if screenshot is not None:
            # Accept raw bytes OR an already-encoded base64 string
            if isinstance(screenshot, (bytes, bytearray)):
                self.screenshot = base64.b64encode(screenshot).decode()
            else:
                self.screenshot = screenshot

    # ── Serialisation (returned by GET /agent/status) ────────────────────────

    def to_dict(self) -> dict:
        return {
            "job_id":     self.job_id,
            "goal":       self.goal,
            "status":     self.status.value,
            "stage":      self.stage,
            "step":       self.step,
            "max_steps":  self.max_steps,
            "progress":   self.progress,
            "thought":    self.thought,
            "action":     self.action,
            "world":      self.world,
            "history":    self.history,
            "screenshot": self.screenshot,
            "error":      self.error,
            "created_at": self.created_at,
        }


# ── JobManager (singleton) ───────────────────────────────────────────────────

class JobManager:
    """
    Thread-safe in-memory store for all running/completed jobs.

    Usage::

        job = job_manager.create(goal="Open YouTube")
        thread = threading.Thread(target=run_loop, args=(job,), daemon=True)
        thread.start()
    """

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, goal: str, max_steps: int = 20) -> Job:
        job = Job(goal=goal, max_steps=max_steps)
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list_all(self) -> list[dict]:
        with self._lock:
            return [j.to_dict() for j in self._jobs.values()]


# Module-level singleton — import this everywhere
job_manager = JobManager()
