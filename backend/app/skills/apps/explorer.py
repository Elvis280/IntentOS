"""
app/skills/apps/explorer.py

Windows Explorer skill.

Public API:
    open_folder(path: str) -> None
    open_file(path: str)   -> None
    select_in_folder(path: str) -> None   # highlight a file in its parent
"""

import os

from app.skills._windows_native import WINDOWS, shell_open


def _normalise(path: str) -> str:
    """Expand ~ and %VARS%, then absolutise. Returns the canonical path."""
    if not path:
        raise Exception("Path missing.")
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def open_folder(path: str) -> None:
    """Open a folder in Windows Explorer.

    Uses ShellExecuteW('open', path) which is the Windows-native way to
    open a path: it respects the user's default file-manager association,
    handles paths with spaces, and does not require 'explorer' to be on
    PATH (which the previous implementation assumed).
    """
    if not WINDOWS:
        raise Exception("open_folder is only supported on Windows.")
    target = _normalise(path)
    if not os.path.exists(target):
        raise Exception(f"Path does not exist: {path}")
    if not os.path.isdir(target):
        # If the user passed a file, open the parent and select it.
        select_in_folder(target)
        return
    rc = shell_open(target)
    if not rc or rc <= 32:
        raise Exception(f"Failed to open folder in Explorer: {path}")


def open_file(path: str) -> None:
    """Open a file with its default Windows association."""
    if not WINDOWS:
        raise Exception("open_file is only supported on Windows.")
    target = _normalise(path)
    if not os.path.exists(target):
        raise Exception(f"Path does not exist: {path}")
    rc = shell_open(target)
    if not rc or rc <= 32:
        raise Exception(f"Failed to open file: {path}")


def select_in_folder(path: str) -> None:
    """Open the parent of `path` in Explorer with `path` highlighted."""
    if not WINDOWS:
        raise Exception("select_in_folder is only supported on Windows.")
    target = _normalise(path)
    if not os.path.exists(target):
        raise Exception(f"Path does not exist: {path}")
    # /select, <path> is the documented Explorer command-line form.
    rc = shell_open(os.path.dirname(target), f"/select,{target}")
    if not rc or rc <= 32:
        # Some hosts don't honour /select, so fall back to opening the parent.
        parent = os.path.dirname(target)
        if os.path.isdir(parent):
            shell_open(parent)
        else:
            raise Exception(f"Failed to open Explorer for: {path}")
