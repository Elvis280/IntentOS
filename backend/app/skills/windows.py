"""
app/skills/windows.py

Windows desktop skills: launch built-in apps, minimise / switch windows.

Public API (unchanged):
    open_application(name: str) -> bool
    minimize_all()                -> None
    close_active()                -> None
    switch_to(index: int = 1)     -> None
"""

import ctypes
import subprocess
import os
import pyautogui

from app.skills._windows_native import (
    WINDOWS,
    SkillUnavailableError,
    is_process_running,
    resolve_app_path,
    shell_open,
    system32_path,
)

if WINDOWS:
    _kernel32 = ctypes.windll.kernel32
    _user32 = ctypes.windll.user32
else:
    _kernel32 = None
    _user32 = None


def open_application(name: str) -> bool:
    """Launch a native Windows application by executable name.

    Used by the Policy Engine (Rule 2) when the reasoner tries to launch
    a known app via PRESS_KEY or a blind CLICK. The `name` argument is
    the subprocess-friendly executable (e.g. 'calc', 'notepad', 'mspaint',
    'cmd', 'explorer', 'winword', 'excel', 'powerpnt', 'taskmgr',
    'regedit') resolved from app/core/constants.APP_EXECUTABLES.

    Returns True on successful launch, False if the executable cannot be
    located. Raises SkillUnavailableError only on non-Windows hosts.
    """
    if not name:
        raise Exception("Application name missing.")
    if not WINDOWS:
        raise SkillUnavailableError(
            f"open_application({name!r}) requires a Windows host."
        )

    # Built-in UWP/Store apps: ShellExecute on the protocol is more reliable
    # than spawning the WindowsApps path directly. We try direct spawn first
    # (it is faster) and only fall back to shell-open on failure.
    resolved = resolve_app_path(name)
    if resolved:
        try:
            subprocess.Popen([resolved])
            return True
        except OSError:
            pass  # fall through to ShellExecute

    # ShellExecute fallback: works for registered executables by name, and
    # is the canonical way to launch a UWP app.
    rc = shell_open(name if name.lower().endswith(".exe") else name + ".exe")
    if rc and rc > 32:
        return True

    # Special case: 'explorer' should always work because explorer.exe ships
    # in %SystemRoot% (not System32). Try a direct Popen as a last attempt.
    if name.lower() in ("explorer", "explorer.exe"):
        explorer = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "explorer.exe")
        if os.path.isfile(explorer):
            subprocess.Popen(explorer)
            return True

    raise Exception(f"Failed to open application: {name!r} not found on this system.")


def minimize_all() -> None:
    """Minimize all windows (Win + D)."""
    pyautogui.hotkey('win', 'd')


def close_active() -> None:
    """Close the active window (Alt + F4)."""
    pyautogui.hotkey('alt', 'f4')


def switch_to(index: int = 1) -> None:
    """Switch to a recently used window using Alt+Tab.

    `index` is 1-based: 1 selects the most-recent window, 2 the next, etc.
    Caps at 8 to avoid spamming the Alt-Tab switcher indefinitely.
    """
    index = max(1, min(int(index or 1), 8))
    pyautogui.keyDown('alt')
    try:
        for _ in range(index):
            pyautogui.press('tab')
    finally:
        pyautogui.keyUp('alt')
