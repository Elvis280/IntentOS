"""
app/skills/apps/excel.py

Microsoft Excel skill.

Public API (unchanged):
    create_workbook()                   -> bool
    write_cell(sheet_index, cell, value)-> bool
"""

from app.skills._com import require_com, dispatch, get_active


def _excel():
    try:
        return get_active("Excel.Application")
    except Exception:
        return dispatch("Excel.Application")


def create_workbook() -> bool:
    """Create a new Excel workbook."""
    require_com()
    excel = _excel()
    excel.Visible = True
    excel.Workbooks.Add()
    return True


def write_cell(sheet_index: int, cell: str, value: str) -> bool:
    """Write a value to a specific cell (e.g. 'A1')."""
    require_com()
    if not cell:
        raise Exception("Cell reference missing (e.g. 'A1').")
    excel = _excel()
    workbook = excel.ActiveWorkbook
    sheet = workbook.Sheets(sheet_index)
    sheet.Range(cell).Value = value
    return True
