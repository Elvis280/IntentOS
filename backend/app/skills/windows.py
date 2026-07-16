import ctypes
import subprocess
import pyautogui

def open_application(name: str):
    """Launch a native Windows application by executable name.

    Used by the Policy Engine (Rule 2) when the reasoner tries to launch
    a known app via PRESS_KEY or a blind CLICK. The `name` argument is
    the subprocess-friendly executable (e.g. 'calc', 'notepad', 'mspaint',
    'cmd', 'explorer', 'winword', 'excel', 'powerpnt', 'taskmgr',
    'regedit') resolved from app/core/constants.APP_EXECUTABLES.
    """
    if not name:
        raise Exception("Application name missing.")

    try:
        subprocess.Popen(name)
    except Exception as e:
        raise Exception(f"Failed to open application: {e}")

def minimize_all():
    """Minimize all windows (Win + D)."""
    pyautogui.hotkey('win', 'd')

def close_active():
    """Close the active window (Alt + F4)."""
    pyautogui.hotkey('alt', 'f4')

def switch_to(index: int = 1):
    """Switch to a recently used window using Alt+Tab."""
    pyautogui.keyDown('alt')
    for _ in range(index):
        pyautogui.press('tab')
    pyautogui.keyUp('alt')
