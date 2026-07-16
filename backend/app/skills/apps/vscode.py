import subprocess
import os

def open_project(path: str):
    """Open a project path in VS Code."""
    if os.path.exists(path):
        subprocess.Popen(['code', os.path.normpath(path)])
    else:
        raise Exception(f"Path does not exist: {path}")
