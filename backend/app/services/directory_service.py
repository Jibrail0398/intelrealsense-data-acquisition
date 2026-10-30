"""Choosing a destination folder.

The backend runs on the same machine as the browser, so it can open the
operating system's own folder dialog. When no dialog is available (a headless
session, a missing zenity), the frontend falls back to browsing folders through
``list_directory``.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from app.core.exceptions import AppError, UnavailableError
from app.schemas.system import DirectoryEntry, DirectoryListing, PickedDirectory

_DIALOG_TIMEOUT = 600  # seconds; the user may take a while to choose

_TK_SCRIPT = """
import sys, tkinter as tk
from tkinter import filedialog
root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
path = filedialog.askdirectory(initialdir=sys.argv[1] or None, title='Choose destination folder', mustexist=False)
print(path or '', end='')
"""


def pick_directory(initial: str | None = None) -> PickedDirectory:
    start = initial if initial and Path(initial).is_dir() else str(Path.home())
    for method, command in _dialog_commands(start):
        try:
            done = subprocess.run(command, capture_output=True, text=True, timeout=_DIALOG_TIMEOUT)
        except (OSError, subprocess.TimeoutExpired):
            continue
        out = done.stdout.strip()
        if done.returncode == 0:
            return PickedDirectory(path=out or None, method=method)
        # zenity, kdialog and osascript exit 1 when the user cancels.
        if done.returncode == 1 and method != "tkinter":
            return PickedDirectory(path=None, method=method)
    raise UnavailableError("No native folder dialog is available on this system", code="picker_unavailable")


def _dialog_commands(start: str) -> list[tuple[str, list[str]]]:
    system = platform.system()
    commands: list[tuple[str, list[str]]] = []
    if system == "Darwin":
        script = (
            'POSIX path of (choose folder with prompt "Choose destination folder" '
            f'default location POSIX file "{start}")'
        )
        commands.append(("osascript", ["osascript", "-e", script]))
    elif system == "Linux" and (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        if shutil.which("zenity"):
            commands.append(("zenity", ["zenity", "--file-selection", "--directory",
                                        "--title=Choose destination folder", f"--filename={start}/"]))
        if shutil.which("kdialog"):
            commands.append(("kdialog", ["kdialog", "--getexistingdirectory", start]))
    if system == "Windows" or (system == "Linux" and os.environ.get("DISPLAY")):
        commands.append(("tkinter", [sys.executable, "-c", _TK_SCRIPT, start]))
    return commands


def list_directory(raw: str | None) -> DirectoryListing:
    path = Path(raw).expanduser() if raw else Path.home()
    if not path.is_dir():
        raise AppError(f"{path} is not a folder")
    path = path.resolve()
    entries = []
    try:
        for child in sorted(path.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith(".") or not child.is_dir():
                continue
            entries.append(DirectoryEntry(name=child.name, path=str(child)))
    except PermissionError as exc:
        raise AppError(f"No permission to read {path}") from exc
    return DirectoryListing(
        path=str(path),
        parent=str(path.parent) if path.parent != path else None,
        entries=entries,
        shortcuts=_shortcuts(),
    )


def create_directory(parent: str, name: str) -> DirectoryEntry:
    name = name.strip()
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise AppError("Enter a valid folder name")
    target = Path(parent).expanduser() / name
    try:
        target.mkdir(parents=False, exist_ok=False)
    except FileExistsError as exc:
        raise AppError(f'"{name}" already exists here') from exc
    except OSError as exc:
        raise AppError(f"Cannot create folder: {exc.strerror}") from exc
    return DirectoryEntry(name=name, path=str(target.resolve()))


def _shortcuts() -> list[DirectoryEntry]:
    home = Path.home()
    candidates = [("Home", home), ("Documents", home / "Documents"), ("Pictures", home / "Pictures"),
                  ("Desktop", home / "Desktop")]
    if platform.system() == "Linux":
        candidates += [("Media", Path("/media") / home.name), ("Mounts", Path("/mnt"))]
    return [DirectoryEntry(name=n, path=str(p)) for n, p in candidates if p.is_dir()]
