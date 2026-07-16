import pyautogui

def click(x: int, y: int, button: str = 'left'):
    """Click at coordinates."""
    pyautogui.click(x=x, y=y, button=button)

def scroll(clicks: int):
    """Scroll up (positive) or down (negative)."""
    pyautogui.scroll(clicks)
