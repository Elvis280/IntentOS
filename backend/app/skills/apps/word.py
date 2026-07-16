"""
app/skills/apps/word.py

Microsoft Word skill.

Public API (unchanged):
    create_document()           -> bool
    type_text(text: str)        -> bool
    save_document(path: str)    -> bool
"""

from app.skills._com import require_com, dispatch, get_active
from app.skills._windows_native import SkillUnavailableError


def _word():
    try:
        return get_active("Word.Application")
    except Exception:
        return dispatch("Word.Application")


def create_document() -> bool:
    """Create a new Word document."""
    require_com()
    word = _word()
    word.Visible = True
    word.Documents.Add()
    return True


def type_text(text: str) -> bool:
    """Type text into the document at the current selection."""
    require_com()
    if not text:
        return False
    word = _word()
    word.Selection.TypeText(text)
    return True


def save_document(path: str) -> bool:
    """Save the document to the specified path."""
    require_com()
    if not path:
        raise Exception("Path missing.")
    word = _word()
    document = word.ActiveDocument
    document.SaveAs(path)
    return True
