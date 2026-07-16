"""
app/skills/clipboard.py

Native-Windows clipboard via ctypes. No third-party clipboard backend
required, so the skill works on any Windows host, including headless
terminals where pyperclip's tkinter backend is unavailable.

Public API (unchanged):
    copy(text: str) -> None
    paste()         -> str
"""

import ctypes
import sys

from app.skills._windows_native import WINDOWS

# Lazy pyperclip fallback — imported only if the native path fails so we
# do not hard-depend on it.
_pyperclip = None

if WINDOWS:
    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32

    GMEM_MOVEABLE = 0x0002
    CF_UNICODETEXT = 13
    CF_TEXT = 1

    OpenClipboard = _user32.OpenClipboard
    OpenClipboard.argtypes = [ctypes.c_void_p]
    OpenClipboard.restype = ctypes.c_bool

    CloseClipboard = _user32.CloseClipboard
    CloseClipboard.argtypes = []
    CloseClipboard.restype = ctypes.c_bool

    EmptyClipboard = _user32.EmptyClipboard
    EmptyClipboard.argtypes = []
    EmptyClipboard.restype = ctypes.c_bool

    GetClipboardData = _user32.GetClipboardData
    GetClipboardData.argtypes = [ctypes.c_uint]
    GetClipboardData.restype = ctypes.c_void_p

    SetClipboardData = _user32.SetClipboardData
    SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    SetClipboardData.restype = ctypes.c_void_p

    GlobalAlloc = _kernel32.GlobalAlloc
    GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    GlobalAlloc.restype = ctypes.c_void_p

    GlobalLock = _kernel32.GlobalLock
    GlobalLock.argtypes = [ctypes.c_void_p]
    GlobalLock.restype = ctypes.c_void_p

    GlobalUnlock = _kernel32.GlobalUnlock
    GlobalUnlock.argtypes = [ctypes.c_void_p]
    GlobalUnlock.restype = ctypes.c_bool

    GlobalFree = _kernel32.GlobalFree
    GlobalFree.argtypes = [ctypes.c_void_p]
    GlobalFree.restype = ctypes.c_void_p


class _ClipboardError(RuntimeError):
    pass


def _native_copy(text: str) -> None:
    if not WINDOWS:
        raise _ClipboardError("Native clipboard is Windows-only.")
    if not OpenClipboard(None):
        raise _ClipboardError("OpenClipboard failed.")
    try:
        if not EmptyClipboard():
            raise _ClipboardError("EmptyClipboard failed.")
        if text is None:
            return  # empty clipboard
        data = text if isinstance(text, str) else str(text)
        encoded = (data + "\0").encode("utf-16-le")
        size = len(encoded)
        h = GlobalAlloc(GMEM_MOVEABLE, size)
        if not h:
            raise _ClipboardError("GlobalAlloc failed.")
        ptr = GlobalLock(h)
        if not ptr:
            GlobalFree(h)
            raise _ClipboardError("GlobalLock failed.")
        try:
            ctypes.memmove(ptr, encoded, size)
        finally:
            GlobalUnlock(h)
        if not SetClipboardData(CF_UNICODETEXT, h):
            GlobalFree(h)
            raise _ClipboardError("SetClipboardData failed.")
    finally:
        CloseClipboard()


def _native_paste() -> str:
    if not WINDOWS:
        raise _ClipboardError("Native clipboard is Windows-only.")
    if not OpenClipboard(None):
        raise _ClipboardError("OpenClipboard failed.")
    try:
        handle = GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        ptr = GlobalLock(handle)
        if not ptr:
            return ""
        try:
            # Read up to first NUL terminator, two bytes wide.
            text = ctypes.wstring_at(ptr)
        finally:
            GlobalUnlock(handle)
        return text.rstrip("\0")
    finally:
        CloseClipboard()


def _pyperclip_fallback_copy(text: str) -> None:
    global _pyperclip
    if _pyperclip is None:
        import pyperclip as _pc
        _pyperclip = _pc
    _pyperclip.copy(text)


def _pyperclip_fallback_paste() -> str:
    global _pyperclip
    if _pyperclip is None:
        import pyperclip as _pc
        _pyperclip = _pc
    return _pyperclip.paste()


def copy(text: str) -> None:
    """Copy text to clipboard. Uses the native Win32 API first, pyperclip as fallback."""
    if text is None:
        text = ""
    if WINDOWS:
        try:
            _native_copy(text)
            return
        except _ClipboardError:
            pass
    _pyperclip_fallback_copy(text)


def paste() -> str:
    """Read text from clipboard. Uses the native Win32 API first, pyperclip as fallback."""
    if WINDOWS:
        try:
            return _native_paste()
        except _ClipboardError:
            pass
    return _pyperclip_fallback_paste()
