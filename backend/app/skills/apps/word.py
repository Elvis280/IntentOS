import win32com.client

def create_document():
    """Create a new Word document."""
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = True
    word.Documents.Add()
    return True

def type_text(text: str):
    """Type text into the document at the current selection."""
    word = win32com.client.GetActiveObject("Word.Application")
    word.Selection.TypeText(text)
    return True
    
def save_document(path: str):
    """Save the document to the specified path."""
    word = win32com.client.GetActiveObject("Word.Application")
    document = word.ActiveDocument
    document.SaveAs(path)
    return True
