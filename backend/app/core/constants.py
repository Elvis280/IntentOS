"""
app/core/constants.py

Shared lookup tables and thresholds used by the Policy Engine.

Centralising these here means changes to supported sites, apps, or
detection signals only need to be made in one place.
"""

# ---------------------------------------------------------------------------
# Known websites — goal keyword → canonical URL
# Extend this dict as the agent supports more sites.
# ---------------------------------------------------------------------------
WEBSITE_URLS: dict[str, str] = {
    "youtube":       "https://www.youtube.com",
    "google":        "https://www.google.com",
    "gmail":         "https://mail.google.com",
    "github":        "https://www.github.com",
    "twitter":       "https://www.twitter.com",
    "x.com":         "https://www.x.com",
    "facebook":      "https://www.facebook.com",
    "instagram":     "https://www.instagram.com",
    "reddit":        "https://www.reddit.com",
    "netflix":       "https://www.netflix.com",
    "spotify":       "https://open.spotify.com",
    "wikipedia":     "https://www.wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
    "linkedin":      "https://www.linkedin.com",
    "chatgpt":       "https://chat.openai.com",
}

# ---------------------------------------------------------------------------
# Known native Windows apps — goal keyword → subprocess-friendly executable
# ---------------------------------------------------------------------------
APP_EXECUTABLES: dict[str, str] = {
    "calculator":     "calc",
    "calc":           "calc",
    "notepad":        "notepad",
    "paint":          "mspaint",
    "mspaint":        "mspaint",
    "command prompt": "cmd",
    "cmd":            "cmd",
    "terminal":       "cmd",
    "file explorer":  "explorer",
    "explorer":       "explorer",
    "word":           "winword",
    "excel":          "excel",
    "powerpoint":     "powerpnt",
    "task manager":   "taskmgr",
    "registry":       "regedit",
}

# ---------------------------------------------------------------------------
# Words in an action's "thought" or "reason" that reveal a taskbar/icon click
# ---------------------------------------------------------------------------
TASKBAR_SIGNALS: frozenset[str] = frozenset({
    "taskbar",
    "desktop icon",
    "browser icon",
    "start button",
    "system tray",
    "dock",
    "launcher",
    "icon on the",
    "tray icon",
    "pinned",
})

# ---------------------------------------------------------------------------
# Known browser process / window-title fragments used by Rule 1 (Fix 3)
# ---------------------------------------------------------------------------
BROWSER_SIGNALS: frozenset[str] = frozenset({
    "chrome",
    "brave",
    "edge",
    "firefox",
    "opera",
    "safari",
    "vivaldi",
    "chromium",
})
