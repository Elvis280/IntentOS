"""
app/skills/_com.py

Optional pywin32 / comtypes detection. We try pywin32 first (the
historical default), then comtypes as a fallback. If neither is
installed the Office skills still import and report themselves as
unavailable — they never raise at module load time.
"""

import sys

from app.skills._windows_native import SkillUnavailableError

try:
    import win32com.client as _win32com  # type: ignore
    _HAS_PYWIN32 = True
except Exception:
    _win32com = None
    _HAS_PYWIN32 = False

try:
    import comtypes.client as _comtypes_client  # type: ignore
    _HAS_COMTYPES = True
except Exception:
    _comtypes_client = None
    _HAS_COMTYPES = False


def require_com() -> None:
    """Raise SkillUnavailableError if no COM automation library is installed."""
    if not (_HAS_PYWIN32 or _HAS_COMTYPES):
        raise SkillUnavailableError(
            "Microsoft Office automation requires either 'pywin32' or 'comtypes'. "
            "Install with: pip install pywin32"
        )


def dispatch(prog_id: str):
    """Dispatch a COM application by its ProgID, preferring pywin32."""
    require_com()
    if _HAS_PYWIN32:
        return _win32com.Dispatch(prog_id)
    return _comtypes_client.CreateObject(prog_id)


def get_active(prog_id: str):
    """Get a running instance of a COM application by ProgID."""
    require_com()
    if _HAS_PYWIN32:
        return _win32com.GetActiveObject(prog_id)
    return _comtypes_client.GetActiveObject(prog_id)
