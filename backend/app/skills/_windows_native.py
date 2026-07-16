"""
app/skills/_windows_native.py

Windows-native helpers shared by every skill. Kept private (underscore prefix)
so the public skill API stays unchanged.

Provides:
    WINDOWS                       - True if running on a real Windows host.
    system32_path()               - %SystemRoot%\\System32, resolved.
    program_files_paths()         - 64-bit and 32-bit Program Files roots.
    resolve_app_path(exe)         - Resolve an executable via App Paths,
                                    known System32 / Program Files locations,
                                    and finally PATH. Returns an absolute
                                    path string or None.
    shell_open(path)              - ShellExecuteW(NULL, 'open', path, ...)
    list_running_processes()      - Lightweight psutil-free snapshot.
    is_process_running(name)      - True if any process with that name exists.
    SkillUnavailableError         - Raised when a skill is intentionally
                                    unavailable (e.g. missing pywin32).
"""

import ctypes
import os
import shutil
import subprocess
import sys
from typing import List, Optional

WINDOWS = sys.platform == "win32"


# ---------------------------------------------------------------------------
# Windows API: ShellExecuteW
# ---------------------------------------------------------------------------

if WINDOWS:
    _shell32 = ctypes.windll.shell32
    _shell32.ShellExecuteW.restype = ctypes.c_void_p
    _shell32.ShellExecuteW.argtypes = [
        ctypes.c_void_p,   # hwnd
        ctypes.c_wchar_p,  # lpOperation
        ctypes.c_wchar_p,  # lpFile
        ctypes.c_wchar_p,  # lpParameters
        ctypes.c_wchar_p,  # lpDirectory
        ctypes.c_int,      # nShowCmd
    ]


class SkillUnavailableError(RuntimeError):
    """Raised when a skill cannot run on the current host (e.g. missing
    optional native dependency such as pywin32). The executor catches
    this and degrades gracefully instead of failing the whole job.
    """


def system32_path() -> str:
    """Return the absolute path to %SystemRoot%\\System32."""
    if WINDOWS:
        sys_root = os.environ.get("SystemRoot", r"C:\Windows")
        return os.path.join(sys_root, "System32")
    return ""


def program_files_paths() -> List[str]:
    """Return both Program Files roots, 64-bit first then 32-bit."""
    if not WINDOWS:
        return []
    return [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("ProgramW6432", r"C:\Program Files"),
    ]


# ---------------------------------------------------------------------------
# App Paths registry resolution
# ---------------------------------------------------------------------------

if WINDOWS:
    _advapi32 = ctypes.windll.advapi32

    _RegOpenKeyExW = _advapi32.RegOpenKeyExW
    _RegOpenKeyExW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_uint,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    _RegOpenKeyExW.restype = ctypes.c_long

    _RegQueryValueExW = _advapi32.RegQueryValueExW
    _RegQueryValueExW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
    ]
    _RegQueryValueExW.restype = ctypes.c_long

    _RegCloseKey = _advapi32.RegCloseKey
    _RegCloseKey.argtypes = [ctypes.c_void_p]
    _RegCloseKey.restype = ctypes.c_long

    HKEY_CURRENT_USER = 0x80000001
    HKEY_LOCAL_MACHINE = 0x80000000
    KEY_READ = 0x20019


def _reg_query_value(root, sub_key, value_name) -> Optional[str]:
    """Return a REG_SZ value from the registry, or None on any failure."""
    if not WINDOWS:
        return None
    hkey = ctypes.c_void_p()
    rc = _RegOpenKeyExW(root, sub_key, 0, KEY_READ, ctypes.byref(hkey))
    if rc != 0 or not hkey.value:
        return None
    try:
        size = ctypes.c_uint(1024)
        buf = ctypes.create_unicode_buffer(1024)
        typ = ctypes.c_uint(0)
        rc = _RegQueryValueExW(
            hkey, value_name, None, ctypes.byref(typ), buf, ctypes.byref(size)
        )
        if rc != 0:
            return None
        return buf.value
    finally:
        _RegCloseKey(hkey)


# Common, well-known System32 binaries. These do not live in PATH on a default
# Windows install and `subprocess.Popen(name)` will fail for them. Listing
# them explicitly is the cheapest, fastest way to keep skills reliable.
_SYSTEM32_BINARIES = {
    "notepad", "notepad.exe",
    "mspaint", "mspaint.exe",
    "calc", "calc.exe",
    "cmd", "cmd.exe",
    "powershell", "powershell.exe",
    "taskmgr", "taskmgr.exe",
    "regedit", "regedit.exe",
    "explorer", "explorer.exe",
    "wordpad", "wordpad.exe",
}


def resolve_app_path(exe: str) -> Optional[str]:
    """Resolve an executable by name to an absolute path.

    Search order:
        1. Caller-supplied absolute path (returned as-is if it exists).
        2. Windows App Paths registry entries
           (HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\<exe>).
        3. System32 well-known names (e.g. 'notepad', 'calc').
        4. Program Files (**\\<exe>) for any non-built-in app.
        5. PATH (shutil.which) as last resort.

    Returns the first match or None.
    """
    if not exe or not WINDOWS:
        if exe and os.path.isabs(exe) and os.path.isfile(exe):
            return exe
        return None

    name = exe
    if not name.lower().endswith(".exe"):
        name = name + ".exe"

    # 1. Already absolute.
    if os.path.isabs(exe) and os.path.isfile(exe):
        return exe
    if os.path.isabs(name) and os.path.isfile(name):
        return name

    # 2. App Paths registry.
    for root in (HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE):
        for stem in (exe, name):
            reg = _reg_query_value(
                root,
                rf"Software\Microsoft\Windows\CurrentVersion\App Paths\{stem}",
                "",
            )
            if reg and os.path.isfile(reg):
                return reg
            reg = _reg_query_value(
                root,
                rf"Software\Microsoft\Windows\CurrentVersion\App Paths\{stem}",
                "Path",
            )
            if reg:
                candidate = os.path.join(reg, stem)
                if os.path.isfile(candidate):
                    return candidate

    # 3. System32 well-known names.
    stem_lower = exe.lower()
    if stem_lower in _SYSTEM32_BINARIES:
        candidate = os.path.join(system32_path(), name)
        if os.path.isfile(candidate):
            return candidate

    # 4. Program Files lookup (recursive, capped depth).
    for root in program_files_paths():
        candidate = _find_in_tree(root, name, max_depth=4)
        if candidate:
            return candidate

    # 5. PATH.
    which = shutil.which(exe) or shutil.which(name)
    if which and os.path.isfile(which):
        return which

    return None


def _find_in_tree(root: str, target: str, max_depth: int = 3) -> Optional[str]:
    """Walk `root` up to `max_depth` levels looking for `target`."""
    if not os.path.isdir(root):
        return None
    root_depth = root.rstrip(os.sep).count(os.sep)
    try:
        for dirpath, _dirnames, filenames in os.walk(root):
            depth = dirpath.count(os.sep) - root_depth
            if depth > max_depth:
                _dirnames[:] = []
                continue
            if target in filenames:
                return os.path.join(dirpath, target)
    except (PermissionError, OSError):
        return None
    return None


# ---------------------------------------------------------------------------
# ShellExecute wrapper
# ---------------------------------------------------------------------------

def shell_open(path: str, arguments: str = "", show_cmd: int = 1) -> Optional[int]:
    """Open `path` with the shell (ShellExecuteW). Returns the HINSTANCE
    returned by the API (>32 = success, <=32 = error code) or None on
    non-Windows. `show_cmd` is the standard SW_* value (1 = SW_SHOWNORMAL).
    """
    if not WINDOWS:
        return None
    if not path:
        return None
    result = _shell32.ShellExecuteW(None, "open", path, arguments, None, show_cmd)
    if isinstance(result, int):
        return result
    return int(result) if result else 0


# ---------------------------------------------------------------------------
# Process inspection (no psutil dependency)
# ---------------------------------------------------------------------------

def list_running_processes() -> List[str]:
    """Return a snapshot of executable names of running processes.

    Implementation: `tasklist /FO CSV /NH`, parsed robustly. We deliberately
    avoid psutil to keep the venv lean.
    """
    if not WINDOWS:
        return []
    try:
        out = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=3,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []
    names = []
    for line in (out.stdout or "").splitlines():
        line = line.strip().strip('"')
        if not line:
            continue
        first = line.split('","', 1)[0]
        if first:
            names.append(first.lower())
    return names


def is_process_running(name: str) -> bool:
    """Case-insensitive check for a process by executable name (e.g. 'notepad.exe')."""
    if not name or not WINDOWS:
        return False
    target = name.lower()
    if not target.endswith(".exe"):
        target += ".exe"
    return target in list_running_processes()


# ---------------------------------------------------------------------------
# Display bounds
# ---------------------------------------------------------------------------

def screen_size() -> tuple:
    """Return (width, height) of the primary display, or (0, 0) on error."""
    if not WINDOWS:
        return (0, 0)
    try:
        user32 = ctypes.windll.user32
        return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    except Exception:
        return (0, 0)
