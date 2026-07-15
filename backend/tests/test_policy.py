"""Unit tests for the PolicyEngine."""
from app.main import app
from app.services.policy import policy

print("Imports OK")

# ── Rule 4 ──────────────────────────────────────────────────────────────────
done = {"action": "DONE", "parameters": {}}
assert policy.apply("Open YouTube", {}, [], done) is done
print("Rule 4  DONE passthrough                         : PASS")

# ── Rule 1 — y > 930 heuristic ──────────────────────────────────────────────
click_bottom = {
    "action": "CLICK",
    "parameters": {"x": 612, "y": 966},
    "thought": "Click the Chrome icon",
    "reason": "Open browser",
}
r = policy.apply("Open YouTube", {"applications": []}, [], click_bottom)
assert r["action"] == "USE_SKILL", r["action"]
assert r["parameters"]["skill"] == "browser"
assert r["parameters"]["function"] == "open_url"
assert "youtube" in r["parameters"]["args"]["url"]
print("Rule 1  CLICK(y>930) -> USE_SKILL(browser)        : PASS")

# ── Rule 1 — thought mentions taskbar ───────────────────────────────────────
click_text = {
    "action": "CLICK",
    "parameters": {"x": 400, "y": 500},
    "thought": "Click the browser icon on the taskbar to open Chrome",
    "reason": "Taskbar",
}
r = policy.apply("Open Google", {"applications": []}, [], click_text)
assert r["action"] == "USE_SKILL", r["action"]
assert r["parameters"]["skill"] == "browser"
assert r["parameters"]["function"] == "open_url"
assert "google" in r["parameters"]["args"]["url"]
print("Rule 1  CLICK(thought:taskbar) -> USE_SKILL       : PASS")

# ── Rule 1 — skipped when browser already open ──────────────────────────────
r = policy.apply("Open Google", {"applications": ["Google Chrome"]}, [], click_text)
assert r["action"] == "CLICK", r["action"]
print("Rule 1  skipped when browser already running      : PASS")

# ── Rule 2 — PRESS_KEY for native app ───────────────────────────────────────
press_win = {
    "action": "PRESS_KEY",
    "parameters": {"key": "win"},
    "thought": "Open start menu",
    "reason": "Search Calculator",
}
r = policy.apply("Open Calculator", {"applications": []}, [], press_win)
assert r["action"] == "USE_SKILL", r["action"]
assert r["parameters"]["skill"] == "windows"
assert r["parameters"]["function"] == "open_application"
assert r["parameters"]["args"]["name"] == "calc"
print("Rule 2  PRESS_KEY -> USE_SKILL(windows)           : PASS")

# ── Rule 2 — skipped when app already running ────────────────────────────────
r = policy.apply("Open Calculator", {"applications": ["Calculator", "Chrome"]}, [], press_win)
assert r["action"] == "PRESS_KEY", r["action"]
print("Rule 2  skipped when app already in world.apps    : PASS")

# ── Rule 2 — CLICK for Notepad ──────────────────────────────────────────────
click_notepad = {
    "action": "CLICK",
    "parameters": {"x": 100, "y": 100},
    "thought": "Look for Notepad",
    "reason": "Open Notepad",
}
r = policy.apply("Open Notepad", {"applications": []}, [], click_notepad)
assert r["action"] == "USE_SKILL", r["action"]
assert r["parameters"]["skill"] == "windows"
assert r["parameters"]["function"] == "open_application"
assert r["parameters"]["args"]["name"] == "notepad"
print("Rule 2  CLICK -> USE_SKILL(windows)               : PASS")

# ── Rule 5 — Search goal ────────────────────────────────────────────────────
r = policy.apply("Search Python decorators", {"applications": []}, [], click_notepad)
assert r["action"] == "USE_SKILL", r["action"]
assert r["parameters"]["skill"] == "browser"
assert r["parameters"]["function"] == "search_google"
assert r["parameters"]["args"]["query"] == "Python decorators"
print("Rule 5  Search -> USE_SKILL(browser.search_google): PASS")

# ── Rule 3 — 3 identical CLICKs -> WAIT ─────────────────────────────────────
history_3 = [
    {"action": {"action": "CLICK", "parameters": {"x": 650, "y": 20}}, "verified": False},
    {"action": {"action": "CLICK", "parameters": {"x": 652, "y": 18}}, "verified": False},
    {"action": {"action": "CLICK", "parameters": {"x": 648, "y": 22}}, "verified": False},
]
click_tab = {
    "action": "CLICK",
    "parameters": {"x": 651, "y": 19},
    "thought": "Click tab",
    "reason": "Bring tab to focus",
}
r = policy.apply("some other goal", {"applications": []}, history_3, click_tab)
assert r["action"] == "REASON_AGAIN", r["action"]
print("Rule 3  CLICK x3 -> REASON_AGAIN                  : PASS")

# ── Rule 3 — 2 CLICKs = passthrough ─────────────────────────────────────────
r = policy.apply("some other goal", {"applications": []}, history_3[:2], click_tab)
assert r["action"] == "CLICK", r["action"]
print("Rule 3  CLICK x2 = passthrough (below threshold)  : PASS")

print()
print("All policy unit tests PASSED.")
