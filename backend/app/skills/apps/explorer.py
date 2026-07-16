import subprocess
import os

def open_folder(path: str):
    """Open a folder in Windows Explorer."""
    if os.path.exists(path):
        subprocess.Popen(f'explorer "{os.path.normpath(path)}"')
    else:
        raise Exception(f"Path does not exist: {path}")
