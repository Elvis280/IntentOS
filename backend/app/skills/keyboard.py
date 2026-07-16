import pyautogui

def type_text(text: str, interval: float = 0.05):
    """Type text out on the keyboard."""
    pyautogui.write(text, interval=interval)

def press_shortcut(keys: list):
    """Press a keyboard shortcut (e.g. ['ctrl', 'c'])."""
    pyautogui.hotkey(*keys)
