"""
app/skills/apps/powerpoint.py

Microsoft PowerPoint skill.

Public API (unchanged):
    create_presentation()              -> bool
    add_slide(title, content)          -> bool
    present()                          -> bool
"""

from app.skills._com import require_com, dispatch, get_active


def _ppt():
    try:
        return get_active("PowerPoint.Application")
    except Exception:
        return dispatch("PowerPoint.Application")


def create_presentation() -> bool:
    """Create a new PowerPoint presentation."""
    require_com()
    ppt = _ppt()
    ppt.Visible = True
    ppt.Presentations.Add()
    return True


def add_slide(title: str = "", content: str = "") -> bool:
    """Add a slide with a title and content."""
    require_com()
    ppt = _ppt()
    presentation = ppt.ActivePresentation
    # 1 = ppLayoutText (Title and Body)
    slide = presentation.Slides.Add(presentation.Slides.Count + 1, 1)
    if title:
        slide.Shapes.Title.TextFrame.TextRange.Text = title
    if content:
        # Assuming the second shape is the body
        slide.Shapes(2).TextFrame.TextRange.Text = content
    return True


def present() -> bool:
    """Start the slideshow."""
    require_com()
    ppt = _ppt()
    presentation = ppt.ActivePresentation
    presentation.SlideShowSettings.Run()
    return True
