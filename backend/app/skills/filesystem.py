"""
app/skills/filesystem.py

Filesystem skill: read, write, list. Path normalisation, encoding
defaults, and explicit error types are all applied here so the
executor and verifier can react deterministically.

Public API (unchanged):
    read_file(path: str)         -> str
    write_file(path: str, content: str) -> None
    list_directory(path: str)    -> list
"""

import os
from typing import List, Union


_DEFAULT_ENCODING = "utf-8"


def _normalise(path: str) -> str:
    if not path:
        raise Exception("Path missing.")
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def read_file(path: str, encoding: str = _DEFAULT_ENCODING) -> str:
    """Read contents of a text file. Raises FileNotFoundError, PermissionError,
    IsADirectoryError, or UnicodeDecodeError — none of which are caught here,
    so the executor can surface them to the verifier with full context."""
    target = _normalise(path)
    if not os.path.exists(target):
        raise FileNotFoundError(f"File not found: {path}")
    if not os.path.isfile(target):
        raise IsADirectoryError(f"Not a regular file: {path}")
    with open(target, "r", encoding=encoding) as f:
        return f.read()


def write_file(
    path: str,
    content: str,
    encoding: str = _DEFAULT_ENCODING,
    create_dirs: bool = False,
) -> None:
    """Write contents to a text file. Overwrites by default.

    If `create_dirs` is True, parent directories are created automatically.
    """
    target = _normalise(path)
    parent = os.path.dirname(target)
    if create_dirs and parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(target, "w", encoding=encoding) as f:
        f.write(content)


def list_directory(path: str = ".") -> List[str]:
    """List entries in a directory. Returns basenames only (matches
    os.listdir semantics) — call os.path.join if you need full paths."""
    target = _normalise(path)
    if not os.path.exists(target):
        raise FileNotFoundError(f"Directory not found: {path}")
    if not os.path.isdir(target):
        raise NotADirectoryError(f"Not a directory: {path}")
    return os.listdir(target)
