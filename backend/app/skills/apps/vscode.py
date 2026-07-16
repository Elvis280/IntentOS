"""
app/skills/apps/vscode.py

Visual Studio Code skill.

Public API:
    open_project(path: str) -> bool
"""

import os
import subprocess

from app.skills._windows_native import (
    WINDOWS,
    resolve_app_path,
)


def _find_code_executable() -> str | None:
    """Locate the VS Code executable on this machine.

    Search order:
        1. Windows App Paths registry (HKCU / HKLM).
        2. Standard install directories.
        3. PATH (the 'code' / 'code.cmd' shim).
    """
    for stem in ("Code.exe", "code.exe"):
        for root in (
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        ):
            if not root:
                continue
            # Microsoft VS Code\Code.exe OR Microsoft VS Code\bin\code.cmd
            candidate = os.path.join(root, "Microsoft VS Code", stem)
            if os.path.isfile(candidate):
                return candidate
            candidate_bin = os.path.join(root, "Microsoft VS Code", "bin", "code.cmd")
            if os.path.isfile(candidate_bin):
                return candidate_bin

    resolved = resolve_app_path("code")
    if resolved and os.path.isfile(resolved):
        return resolved
    return None


def open_project(path: str) -> bool:
    """Open a project path in VS Code.

    Returns True on success. Raises on missing path. Raises a clear error
    if VS Code itself is not installed.
    """
    if not WINDOWS:
        raise Exception("open_project is only supported on Windows.")
    if not path:
        raise Exception("Path missing.")
    target = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
    if not os.path.exists(target):
        raise Exception(f"Path does not exist: {path}")

    code = _find_code_executable()
    if not code:
        raise Exception(
            "VS Code is not installed (or 'code' is not on PATH). "
            "Install it from https://code.visualstudio.com/."
        )

    try:
        # code.cmd requires shell=True; Code.exe works with shell=False.
        if code.lower().endswith((".cmd", ".bat")):
            subprocess.Popen(code, args=[target], shell=True)
        else:
            subprocess.Popen([code, target])
    except OSError as exc:
        raise Exception(f"Failed to launch VS Code: {exc}") from exc
    return True
