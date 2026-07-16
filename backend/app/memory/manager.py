"""
Working Memory Manager.

Maintains a deterministic, job-scoped memory that consolidates:
- Execution state (goal, step)
- Workspace context
- Action history (successes, failures, decisions)
- UI element awareness
- World and Context snapshots

Everything is discarded when the job finishes. The manager exposes
a clean API: update, remember, forget, clear, get.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.memory.models import WorkingMemoryState


_MAX_RECENT_DECISIONS = 10
_MAX_RECENTLY_USED_UI = 15


class WorkingMemoryManager:
    """
    Instantiated once per job. Automatically discarded when the job thread ends.
    """

    def __init__(self) -> None:
        self._state = WorkingMemoryState()

    # ── Core update (called every loop iteration) ─────────────────────────────

    def update(
        self,
        *,
        goal: str,
        step: int,
        world_snapshot: Dict[str, Any],
        context_snapshot: Dict[str, Any],
        ui_elements: List[Dict[str, Any]],
        history: List[Dict[str, Any]],
        plan: Optional[Dict[str, Any]] = None,
        active_plan_step: Optional[Dict[str, Any]] = None,
        plan_progress: Optional[Dict[str, Any]] = None,
    ) -> WorkingMemoryState:
        """
        Consolidate all available information into the working memory state.
        Called once per iteration, after World → UI Intelligence → Context.
        """
        self._state.current_goal = goal
        self._state.current_step = step
        self._state.current_world_snapshot = world_snapshot
        self._state.current_context = context_snapshot
        self._state.current_ui_elements = ui_elements
        
        # Plan state
        self._state.current_plan = plan
        self._state.active_plan_step = active_plan_step
        self._state.plan_progress = plan_progress

        # Workspace awareness from context
        self._state.current_workspace = context_snapshot.get("current_workspace")
        self._state.focused_window = context_snapshot.get("active_window_title")

        # Selected object from context
        sel = context_snapshot.get("current_selection")
        self._state.selected_object = sel

        # Derive action history
        self._update_action_history(history)

        return self._state

    # ── Selective remember / forget ───────────────────────────────────────────

    def remember(self, key: str, value: Any) -> None:
        """Store an arbitrary key-value pair in memory."""
        if key == "pending_confirmation":
            self._state.pending_confirmation = value
        elif hasattr(self._state, key):
            setattr(self._state, key, value)
        # We could also use a metadata dict here in the future if needed

    def forget(self, key: str) -> None:
        """Remove a specific remembered value."""
        if key == "pending_confirmation":
            self._state.pending_confirmation = None
        elif hasattr(self._state, key):
            setattr(self._state, key, None)

    def clear(self) -> None:
        """Wipe all working memory. Called when the job finishes."""
        self._state = WorkingMemoryState()

    # ── Read API ──────────────────────────────────────────────────────────────

    def get(self) -> WorkingMemoryState:
        """Return the current working memory state."""
        return self._state

    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Return the currently selected object, if any."""
        return self._state.selected_object

    def get_recent_actions(self) -> List[Dict[str, Any]]:
        """Return the list of recent runtime decisions."""
        return list(self._state.recent_decisions)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for passing to the Reasoner."""
        return self._state.model_dump()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _update_action_history(self, history: List[Dict[str, Any]]) -> None:
        """Derive last_successful, last_failed, recent_decisions from job history."""
        self._state.last_successful_action = None
        self._state.last_failed_action = None

        for entry in reversed(history):
            action = entry.get("action", {})
            verified_data = entry.get("verified", True)
            if isinstance(verified_data, dict):
                verified = verified_data.get("verified", True)
            else:
                verified = bool(verified_data)

            if verified and self._state.last_successful_action is None:
                self._state.last_successful_action = action
            if not verified and self._state.last_failed_action is None:
                self._state.last_failed_action = action

            if self._state.last_successful_action and self._state.last_failed_action:
                break

        # Recent decisions = last N history entries
        self._state.recent_decisions = history[-_MAX_RECENT_DECISIONS:]

        # Track recently used UI elements based on CLICK actions
        recently_used: List[Dict[str, Any]] = []
        for entry in reversed(history[-_MAX_RECENTLY_USED_UI:]):
            action = entry.get("action", {})
            if action.get("action") == "CLICK":
                params = action.get("parameters", {})
                recently_used.append({
                    "type": "clicked_element",
                    "x": params.get("x"),
                    "y": params.get("y"),
                    "verified": entry.get("verified", True),
                })
        self._state.recently_used_ui_elements = recently_used
