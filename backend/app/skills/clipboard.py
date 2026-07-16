import pyperclip

def copy(text: str):
    """Copy text to clipboard."""
    pyperclip.copy(text)

def paste() -> str:
    """Read text from clipboard."""
    return pyperclip.paste()
