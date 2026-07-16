"""
Working Memory models.

Working Memory exists ONLY during the current Job execution.
It is NOT long-term memory. Everything is discarded when the Job finishes.
It provides a consolidated, deterministic snapshot of the current execution state
for the Reasoner to consume.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkingMemoryState(BaseModel):
    """
    The full working memory snapshot passed to the Reasoner each iteration.
    All fields are deterministically populated — no embeddings, no vector DB, no LLM.
    """

    # ── Execution state ──────────────────────────────────────────────────────
    current_goal: Optional[str] = None
    current_step: int = 0
    
    # ── Plan state ───────────────────────────────────────────────────────────
    current_plan: Optional[Dict[str, Any]] = None
    active_plan_step: Optional[Dict[str, Any]] = None
    plan_progress: Optional[Dict[str, Any]] = None

    # ── Workspace awareness ──────────────────────────────────────────────────
    current_workspace: Optional[str] = None
    focused_window: Optional[str] = None
    selected_object: Optional[Dict[str, Any]] = None

    # ── Action history ───────────────────────────────────────────────────────
    last_successful_action: Optional[Dict[str, Any]] = None
    last_failed_action: Optional[Dict[str, Any]] = None
    recent_decisions: List[Dict[str, Any]] = Field(default_factory=list)

    # ── UI awareness ─────────────────────────────────────────────────────────
    current_ui_elements: List[Dict[str, Any]] = Field(default_factory=list)
    recently_used_ui_elements: List[Dict[str, Any]] = Field(default_factory=list)

    # ── Context & World snapshots ────────────────────────────────────────────
    current_context: Optional[Dict[str, Any]] = None
    current_world_snapshot: Optional[Dict[str, Any]] = None

    # ── Confirmation state ───────────────────────────────────────────────────
    pending_confirmation: Optional[Dict[str, Any]] = None
