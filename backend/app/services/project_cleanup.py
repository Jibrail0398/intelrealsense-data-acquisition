"""Removing a deleted project's images from disk.

Only folders the app created for this project are removed:
``{destination}/{format}/{class}/`` for every class the project has or had,
plus folders its captures were written to. Format folders and the destination
itself are removed only when that leaves them empty, so files the user keeps
next to the dataset are never touched. A class folder that another project
also writes to is not removed; only this project's own files in it are.
"""

import shutil
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from app.models import CaptureRecord, Project
from app.services.image_writer import FORMATS, class_dir


@dataclass
class CleanupResult:
    deleted_files: int = 0
    deleted_folders: int = 0
    errors: list[str] = field(default_factory=list)


def owned_dirs(project: Project, records: Iterable[CaptureRecord]) -> set[Path]:
    """Every class folder this project writes to, resolved."""
    records = list(records)
    names = {c.name for c in project.classes} | {r.class_name for r in records}
    dirs = {class_dir(project.destination_dir, f, n) for f in FORMATS.values() for n in names}
    dirs |= {Path(p).parent for r in records for p in r.files.values()}
    return {d.resolve() for d in dirs}


def delete_project_files(
    project: Project,
    records: list[CaptureRecord],
    protected: set[Path],
) -> CleanupResult:
    result = CleanupResult()
    targets = owned_dirs(project, records)

    # This project's own files go wherever they are, shared folder or not.
    for record in records:
        for raw in record.files.values():
            path = Path(raw)
            try:
                if path.is_file():
                    path.unlink()
                    result.deleted_files += 1
            except OSError as exc:
                result.errors.append(f"{path}: {exc.strerror or exc}")

    # Whole class folders, unless another project uses the same one.
    for directory in sorted(targets):
        if directory in protected or not directory.is_dir():
            continue
        try:
            files = sum(1 for p in directory.rglob("*") if p.is_file())
            folders = 1 + sum(1 for p in directory.rglob("*") if p.is_dir())
            shutil.rmtree(directory)
            result.deleted_files += files
            result.deleted_folders += folders
        except OSError as exc:
            result.errors.append(f"{directory}: {exc.strerror or exc}")

    # Format folders, then the destination, only if now empty.
    parents = {d.parent for d in targets} | {d.parent.parent for d in targets}
    for directory in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
            result.deleted_folders += 1
        except OSError:
            pass  # not empty, or already gone
    return result
