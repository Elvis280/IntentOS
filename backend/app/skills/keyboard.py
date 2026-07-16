"""
app/skills/keyboard.py

Keyboard automation via pyautogui. Kept thin; the only responsibilities
that live here are argument validation and Unicode-safe text entry.

Public API (unchanged):
    type_text(text: str, interval: float = 0.05) -> None
    press_shortcut(keys: list)                    -> None
"""

from typing import Iterable

import pyautogui


_ALLOWED_KEYS = {
    "ctrl", "control", "alt", "shift", "win", "windows", "command", "cmd",
    "enter", "return", "tab", "escape", "esc", "space", "backspace", "delete",
    "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "printscreen", "insert", "capslock", "numlock", "scrolllock",
}


def _paste_unicode(text: str) -> None:
    """Paste `text` through the clipboard (handles non-ASCII safely).

    Defined here as a local helper to avoid a circular import between
    `clipboard` and `keyboard`. clipboard is the lower-level layer.
    """
    import importlib
    clip = importlib.import_module("app.skills.clipboard")
    prev = ""
    try:
        prev = clip.paste()
    except Exception:
        prev = ""
    clip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    # Best-effort restore of prior clipboard content.
    try:
        if prev:
            clip.copy(prev)
    except Exception:
        pass


def type_text(text: str, interval: float = 0.05) -> None:
    """Type text out on the keyboard.

    `interval` is clamped to [0, 1.0] seconds to prevent runaway pauses.
    pyautogui.write is used for ASCII; non-ASCII characters are entered via
    the clipboard to avoid keyboard-layout issues.
    """
    if text is None:
        return
    interval = max(0.0, min(float(interval or 0.0), 1.0))

    if text.isascii():
        pyautogui.write(text, interval=interval)
        return

    _paste_unicode(text)


def press_shortcut(keys: list) -> None:
    """Press a keyboard shortcut (e.g. ['ctrl', 'c']).

    Raises ValueError on empty input or an unrecognised key, so the
    executor's error message is clear instead of pyautogui's generic one.
    """
    if not keys:
        raise ValueError("press_shortcut requires at least one key.")
    keys = list(keys)
    for k in keys:
        if not isinstance(k, str) or not k:
            raise ValueError(f"Invalid key in shortcut: {k!r}")
        if k.lower() not in _ALLOWED_KEYS and len(k) > 1:
            # Single chars are fine (letters, digits, symbols).
            # Multi-char must be a known name.
            raise ValueError(f"Unrecognised key: {k!r}")
    pyautogui.hotkey(*keys)
