"""
app/skills/mouse.py

Mouse automation via pyautogui, with bounds validation against the
primary display so the verifier can recover from off-screen clicks
instead of crashing the agent loop.

Public API (unchanged):
    click(x: int, y: int, button: str = 'left') -> None
    scroll(clicks: int)                          -> None
"""

import pyautogui

from app.skills._windows_native import WINDOWS, screen_size


class OutOfBoundsError(ValueError):
    """Raised when a click coordinate is outside the primary display."""


def _validate_coords(x, y) -> tuple:
    x = int(x)
    y = int(y)
    if WINDOWS:
        w, h = screen_size()
        if w and h and not (0 <= x < w and 0 <= y < h):
            raise OutOfBoundsError(
                f"Click coordinates ({x}, {y}) outside primary display ({w}x{h})."
            )
    return x, y


def click(x: int, y: int, button: str = 'left') -> None:
    """Click at coordinates.

    `button` must be one of: 'left', 'right', 'middle' (case-insensitive).
    """
    if button not in ('left', 'right', 'middle'):
        raise ValueError(f"Invalid mouse button: {button!r}")
    x, y = _validate_coords(x, y)
    pyautogui.click(x=x, y=y, button=button)


def scroll(clicks: int) -> None:
    """Scroll up (positive) or down (negative)."""
    clicks = int(clicks)
    if clicks == 0:
        return
    pyautogui.scroll(clicks)
