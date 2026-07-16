import win32com.client

def create_workbook():
    """Create a new Excel workbook."""
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    excel.Workbooks.Add()
    return True

def write_cell(sheet_index: int, cell: str, value: str):
    """Write a value to a specific cell (e.g. 'A1')."""
    excel = win32com.client.GetActiveObject("Excel.Application")
    workbook = excel.ActiveWorkbook
    sheet = workbook.Sheets(sheet_index)
    sheet.Range(cell).Value = value
    return True
