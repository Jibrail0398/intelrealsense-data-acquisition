"""File and folder naming rules for dataset output."""

import re
from pathlib import Path

# Characters that are illegal in file names on Windows, macOS or Linux.
_ILLEGAL = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
INDEX_DIGITS = 4


def validate_class_name(name: str) -> str:
    cleaned = " ".join(name.split())
    if not cleaned:
        raise ValueError("Class name cannot be empty")
    if _ILLEGAL.search(cleaned):
        raise ValueError('Class name cannot contain \\ / : * ? " < > |')
    if cleaned.startswith(".") or cleaned in {".", ".."}:
        raise ValueError("Class name cannot start with a dot")
    if len(cleaned) > 120:
        raise ValueError("Class name is too long (max 120 characters)")
    return cleaned


def image_name(class_name: str, index: int) -> str:
    return f"{class_name}-{index:0{INDEX_DIGITS}d}"


def parse_index(stem: str, class_name: str) -> int | None:
    prefix = f"{class_name}-"
    if not stem.startswith(prefix):
        return None
    tail = stem[len(prefix):]
    return int(tail) if tail.isdigit() else None


def max_index_in_dir(directory: Path, class_name: str) -> int:
    """Highest image index already on disk for this class, 0 if none."""
    if not directory.is_dir():
        return 0
    best = 0
    for entry in directory.iterdir():
        if entry.is_file():
            idx = parse_index(entry.stem, class_name)
            if idx is not None and idx > best:
                best = idx
    return best
