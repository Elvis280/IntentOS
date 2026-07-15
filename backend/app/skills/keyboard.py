"""
app/skills/keyboard.py

Keyboard automation skill for IntentOS.
"""
import pyautogui
from app.executor.executor import Executor

_executor = Executor()

def press(key: str):
    """Press a single keyboard key."""
    _executor.execute({
        "action": "PRESS_KEY",
        "parameters": {"key": key}
    })

def hotkey(*keys):
    """Press a combination of keys (e.g. 'ctrl', 'c')."""
    pyautogui.hotkey(*keys)

def type_text(text: str):
    """Type text out."""
    _executor.execute({
        "action": "TYPE",
        "parameters": {"text": text}
    })

def copy():
    """Copy current selection to clipboard."""
    hotkey("ctrl", "c")

def paste():
    """Paste from clipboard."""
    hotkey("ctrl", "v")
