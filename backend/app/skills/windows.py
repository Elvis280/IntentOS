"""
app/skills/windows.py

Windows application management skill for IntentOS.
"""
import subprocess
import pygetwindow as gw
from app.executor.executor import Executor

_executor = Executor()

def open_application(name: str):
    """Open a Windows application using its executable name."""
    _executor.execute({
        "action": "OPEN_APPLICATION",
        "parameters": {"target": name}
    })

def close_application(name: str):
    """Forcefully close an application by its executable name."""
    subprocess.run(["taskkill", "/IM", f"{name}.exe", "/F"], capture_output=True)

def switch_application(name: str):
    """Switch focus to an already open application by matching its window title."""
    windows = gw.getWindowsWithTitle(name)
    if windows:
        # Try to activate the first matching window
        try:
            windows[0].activate()
        except Exception as e:
            print(f"Failed to activate window: {e}")
