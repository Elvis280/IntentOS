import win32com.client

def create_presentation():
    """Create a new PowerPoint presentation."""
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    ppt.Presentations.Add()
    return True

def add_slide(title: str = "", content: str = ""):
    """Add a slide with a title and content."""
    ppt = win32com.client.GetActiveObject("PowerPoint.Application")
    presentation = ppt.ActivePresentation
    # 1 = ppLayoutText (Title and Body)
    slide = presentation.Slides.Add(presentation.Slides.Count + 1, 1)
    if title:
        slide.Shapes.Title.TextFrame.TextRange.Text = title
    if content:
        # Assuming the second shape is the body
        slide.Shapes(2).TextFrame.TextRange.Text = content
    return True

def present():
    """Start the slideshow."""
    ppt = win32com.client.GetActiveObject("PowerPoint.Application")
    presentation = ppt.ActivePresentation
    presentation.SlideShowSettings.Run()
    return True
