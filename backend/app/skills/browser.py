"""
app/skills/browser.py

Default-browser skills: open a URL, perform a Google search.

Public API:
    navigate(url: str)         -> None
    search(query: str)         -> None
    open_url(url: str)         -> None   # alias used by the Policy engine
    search_google(query: str)  -> None   # alias used by the Policy engine
"""

import os
import subprocess
import webbrowser

from app.skills._windows_native import WINDOWS, shell_open


def _open_in_default_browser(url: str) -> bool:
    """Try webbrowser first (Python's stdlib default-browser lookup), then
    fall back to ShellExecute so an empty or misconfigured association
    still succeeds.

    Returns True if either path succeeded, False otherwise. Never raises.
    """
    if not url:
        return False

    # 1. webbrowser.open honours BROWSER env var and the user's default
    #    association. Use try/except because the stdlib will raise on
    #    some misconfigured Windows hosts.
    try:
        if webbrowser.open(url, new=2, autoraise=True):
            return True
    except webbrowser.Error:
        pass

    # 2. ShellExecute: works even when Python's webbrowser module cannot
    #    locate a default (rare, but observed on locked-down terminals).
    if WINDOWS:
        rc = shell_open(url)
        if rc and rc > 32:
            return True

    # 3. Last resort: launch msedge via App Paths (ships with Windows 10/11).
    if WINDOWS:
        edge_candidates = (
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        )
        for edge in edge_candidates:
            if os.path.isfile(edge):
                try:
                    subprocess.Popen([edge, url])
                    return True
                except OSError:
                    continue
    return False


def navigate(url: str) -> None:
    """Navigate to a URL using the default browser."""
    if not url:
        raise Exception("URL missing.")
    if not _open_in_default_browser(url):
        raise Exception(f"Failed to open URL: no default browser available for {url!r}.")


def search(query: str) -> None:
    """Search Google in the default browser."""
    if not query:
        raise Exception("Search query missing.")
    from urllib.parse import quote_plus
    navigate(f"https://www.google.com/search?q={quote_plus(query)}")


# ── Policy-facing aliases ──────────────────────────────────────────────────
# The Policy Engine (Rules 1 and 5) calls these exact names. Keep them as
# thin wrappers so the skill stays a single, well-defined unit.

def open_url(url: str) -> None:
    """Policy Rule 1 alias for navigate()."""
    navigate(url)


def search_google(query: str) -> None:
    """Policy Rule 5 alias for search()."""
    search(query)
