"""
app/services/policy.py

Deterministic Policy Engine for IntentOS.

Sits between the Reasoner and the Executor. Receives the action proposed
by the Reasoner and either passes it through unchanged or overrides it
based on hard, rule-based logic the LLM cannot guarantee.

Rules (applied in order):
    Rule 4 — DONE is always returned unchanged.
    Rule 3 — Repeated CLICK failures → REASON_AGAIN (skip execution).
    Rule 1 — Intercept taskbar/icon CLICKs when the goal is a website
              AND no browser is already open.
    Rule 2 — Intercept PRESS_KEY / CLICK when the goal is a native app
              and that app is not already running.
"""

import logging
from typing import Optional

from app.core.constants import (
    APP_EXECUTABLES,
    BROWSER_SIGNALS,
    TASKBAR_SIGNALS,
    WEBSITE_URLS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds — kept local; they are policy behaviour, not lookup data
# ---------------------------------------------------------------------------

# Pixels above the bottom of the screen considered the taskbar region.
# 1080p taskbar ≈ y > 1040; 930 is safe on lower-res screens.
TASKBAR_Y_THRESHOLD = 930

# How many times a CLICK at the same region must appear in history
# before Rule 3 triggers.
CLICK_FAIL_THRESHOLD = 3

# Radius (pixels) within which two CLICKs are considered the same location.
CLICK_FUZZY_RADIUS = 15

# Sentinel action type returned by Rule 3 — agent.py skips execution for this.
REASON_AGAIN = "REASON_AGAIN"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _detect_website_url(goal: str) -> Optional[str]:
    """Return the URL if the goal is about opening a known website."""
    g = goal.lower()
    for keyword, url in WEBSITE_URLS.items():
        if keyword in g:
            return url
    return None


def _detect_app_executable(goal: str) -> Optional[str]:
    """Return the executable name if the goal is about opening a known app.

    Multi-word keywords are checked first so 'command prompt' beats 'cmd'.
    """
    g = goal.lower()
    for keyword in sorted(APP_EXECUTABLES, key=len, reverse=True):
        if keyword in g:
            return APP_EXECUTABLES[keyword]
    return None


def _is_browser_open(world: dict) -> bool:
    """Return True if a known browser is already running in the world model.

    Checks both the applications list and the active_window title.
    """
    apps_lower = [a.lower() for a in world.get("applications", [])]
    active = world.get("active_window", "").lower()

    candidates = apps_lower + [active]
    return any(
        browser in candidate
        for browser in BROWSER_SIGNALS
        for candidate in candidates
    )


def _is_app_already_running(exe: str, world: dict) -> bool:
    """Return True if the application appears to already be open in the world."""
    apps_lower = [a.lower() for a in world.get("applications", [])]
    # Map executable name back to a display-name fragment to check against
    display_hints = {
        "calc":     "calculator",
        "notepad":  "notepad",
        "mspaint":  "paint",
        "cmd":      "command",
        "explorer": "explorer",
        "winword":  "word",
        "excel":    "excel",
        "powerpnt": "powerpoint",
        "taskmgr":  "task manager",
        "regedit":  "registry",
    }
    hint = display_hints.get(exe, exe)
    return any(hint in app for app in apps_lower)


def _is_taskbar_click(action: dict) -> bool:
    """Return True if the action looks like a click on a taskbar icon."""
    # Check text evidence from the reasoner's own explanation
    text = (
        action.get("thought", "") + " " + action.get("reason", "")
    ).lower()
    if any(signal in text for signal in TASKBAR_SIGNALS):
        return True

    # Heuristic: y-coordinate in the taskbar strip at the bottom
    y = action.get("parameters", {}).get("y") or 0
    if y > TASKBAR_Y_THRESHOLD:
        return True

    return False


def _click_count_in_history(action: dict, history: list) -> int:
    """Count how many times a similar CLICK appears in history."""
    ax = action.get("parameters", {}).get("x", 0)
    ay = action.get("parameters", {}).get("y", 0)
    count = 0
    for entry in history:
        past = entry.get("action", {})
        if past.get("action") != "CLICK":
            continue
        px = past.get("parameters", {}).get("x", 0)
        py = past.get("parameters", {}).get("y", 0)
        if (
            abs(ax - px) <= CLICK_FUZZY_RADIUS
            and abs(ay - py) <= CLICK_FUZZY_RADIUS
        ):
            count += 1
    return count


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------

class PolicyEngine:
    """Deterministic rule layer between the Reasoner and the Executor.

    Call apply() with the full context and the Reasoner's proposed action.
    Returns the action that should actually be executed — either the
    original or an override.

    The special action type REASON_AGAIN instructs agent.py to skip
    executor.execute() and go straight to the next Observe → Reason cycle.
    """

    def apply(
        self,
        goal: str,
        world: dict,
        history: list,
        action: dict,
    ) -> dict:
        """Evaluate all rules and return the final action.

        Rules are applied in this fixed order; first match wins:
            Rule 4  —  DONE passthrough
            Rule 3  —  Repeated CLICK → REASON_AGAIN
            Rule 1  —  Taskbar CLICK for website → OPEN_URL
            Rule 2  —  PRESS_KEY / CLICK for native app → OPEN_APPLICATION

        Args:
            goal:    The original user goal string.
            world:   Current world model dict (from WorldState.model_dump()).
            history: List of {"action": ..., "verified": ...} dicts so far.
            action:  The action dict proposed by the Reasoner.

        Returns:
            The action dict to pass to the Executor (or REASON_AGAIN to skip).
        """
        act = action.get("action")

        # ── Rule 4 ────────────────────────────────────────────────────────────
        # DONE is sacred — never override it.
        if act == "DONE":
            return action

        # ── Rule 3 ────────────────────────────────────────────────────────────
        # This CLICK region has been attempted too many times.
        # Return REASON_AGAIN so the agent skips execution and re-observes,
        # breaking the CLICK → WAIT → CLICK loop that a simple WAIT produces.
        if act == "CLICK":
            count = _click_count_in_history(action, history)
            if count >= CLICK_FAIL_THRESHOLD:
                logger.info(
                    "Rule 3 — CLICK at same region attempted %dx; "
                    "returning REASON_AGAIN.",
                    count,
                )
                return {
                    "thought": "Policy override: repeated CLICK failures detected.",
                    "action":  REASON_AGAIN,
                    "parameters": {},
                    "reason": (
                        "Policy Rule 3: CLICK has failed too many times in this "
                        "region. Skipping execution and re-observing."
                    ),
                }

        # ── Rule 1 ────────────────────────────────────────────────────────────
        # Reasoner tried to click a taskbar/desktop icon to open a website.
        # Only redirect to USE_SKILL when no browser is already open;
        # if a browser is running, the Reasoner should interact with it directly.
        if act == "CLICK":
            url = _detect_website_url(goal)
            if url and _is_taskbar_click(action) and not _is_browser_open(world):
                logger.info(
                    "Rule 1 — Replacing CLICK (taskbar) with USE_SKILL(browser.open_url, %s).", url
                )
                return {
                    "thought": "Policy override: navigating to website directly.",
                    "action":  "USE_SKILL",
                    "parameters": {
                        "skill": "browser",
                        "function": "open_url",
                        "args": {"url": url}
                    },
                    "reason": (
                        "Policy Rule 1: browser skill is preferred over clicking a "
                        "taskbar icon when no browser is already open."
                    ),
                }

        # ── Rule 2 ────────────────────────────────────────────────────────────
        # Reasoner used PRESS_KEY (Win key search) or a blind CLICK to launch
        # a native app. Replace with a direct USE_SKILL call.
        if act in ("PRESS_KEY", "CLICK"):
            exe = _detect_app_executable(goal)
            if exe and not _is_app_already_running(exe, world):
                logger.info(
                    "Rule 2 — Replacing %s with USE_SKILL(windows.open_application, %s).", act, exe
                )
                return {
                    "thought": "Policy override: launching application directly.",
                    "action":  "USE_SKILL",
                    "parameters": {
                        "skill": "windows",
                        "function": "open_application",
                        "args": {"name": exe}
                    },
                    "reason": (
                        f"Policy Rule 2: windows skill is always preferred "
                        f"over {act} for native app goals."
                    ),
                }

        # ── Rule 5 ────────────────────────────────────────────────────────────
        # If the goal is explicitly to search, use the browser skill directly
        # instead of letting the reasoner fumble with opening a browser and typing.
        if act in ("CLICK", "PRESS_KEY"):
            if goal.lower().startswith("search ") and not _is_browser_open(world):
                query = goal[7:].strip()
                logger.info(
                    "Rule 5 — Replacing %s with USE_SKILL(browser.search_google, %s).", act, query
                )
                return {
                    "thought": "Policy override: using browser search skill.",
                    "action":  "USE_SKILL",
                    "parameters": {
                        "skill": "browser",
                        "function": "search_google",
                        "args": {"query": query}
                    },
                    "reason": "Policy Rule 5: Search goals use browser skill directly."
                }

        # No rule matched — pass the action through unchanged
        return action


# Singleton used by api/agent.py
policy = PolicyEngine()
