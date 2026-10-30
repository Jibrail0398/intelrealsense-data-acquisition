"""Output formats and the atomic writer that saves one shot in each of them.

Folder layout produced for a project:

    {destination_dir}/{format.folder}/{class_name}/{class_name}-{index:04d}.{ext}

e.g. ``/data/stunting/png/tidak stunting/tidak stunting-0007.png``.
"""

import io
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import numpy as np

StreamKind = Literal["rgb", "depth"]


@dataclass(frozen=True)
class OutputFormat:
    key: str
    label: str
    kind: StreamKind
    folder: str
    ext: str
    description: str
    encode: Callable[[np.ndarray], bytes]


def _cv_encode(ext: str, params: list[int] | None = None) -> Callable[[np.ndarray], bytes]:
    def encode(image: np.ndarray) -> bytes:
        ok, buf = cv2.imencode(ext, image, params or [])
        if not ok:
            raise RuntimeError(f"OpenCV could not encode {ext}")
        return buf.tobytes()

    return encode


def _npy_encode(depth: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, depth, allow_pickle=False)
    return buffer.getvalue()


FORMATS: dict[str, OutputFormat] = {
    f.key: f
    for f in (
        OutputFormat("jpg", "RGB JPG", "rgb", "jpg", "jpg", "8-bit colour, compressed (quality 95)",
                     _cv_encode(".jpg", [cv2.IMWRITE_JPEG_QUALITY, 95])),
        OutputFormat("png", "RGB PNG", "rgb", "png", "png", "8-bit colour, lossless",
                     _cv_encode(".png", [cv2.IMWRITE_PNG_COMPRESSION, 3])),
        OutputFormat("tiff", "Depth TIFF", "depth", "tiff", "tiff", "16-bit raw depth units",
                     _cv_encode(".tiff")),
        OutputFormat("png16", "Depth PNG 16-bit", "depth", "png16", "png", "16-bit raw depth units, lossless",
                     _cv_encode(".png", [cv2.IMWRITE_PNG_COMPRESSION, 3])),
        OutputFormat("npy", "Depth NPY", "depth", "npy", "npy", "NumPy uint16 array of raw depth units",
                     _npy_encode),
    )
}


def output_path(destination_dir: str | Path, fmt: OutputFormat, class_name: str, name: str) -> Path:
    return Path(destination_dir) / fmt.folder / class_name / f"{name}.{fmt.ext}"


def class_dir(destination_dir: str | Path, fmt: OutputFormat, class_name: str) -> Path:
    return Path(destination_dir) / fmt.folder / class_name


def write_shot(
    destination_dir: str | Path,
    format_keys: list[str],
    class_name: str,
    name: str,
    color: np.ndarray,
    depth: np.ndarray,
) -> dict[str, str]:
    """Write one RGB/depth pair in every format, all or nothing.

    Each file is written to a temporary name and renamed into place only after
    every format has encoded and written successfully, so a failure never
    leaves half a pair on disk.
    """
    staged: list[tuple[Path, Path]] = []
    try:
        for key in format_keys:
            fmt = FORMATS[key]
            target = output_path(destination_dir, fmt, class_name, name)
            if target.exists():
                raise FileExistsError(f"{target} already exists")
            target.parent.mkdir(parents=True, exist_ok=True)
            data = fmt.encode(color if fmt.kind == "rgb" else depth)
            tmp = target.with_name(f".{target.name}.part")
            with open(tmp, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            staged.append((tmp, target))
    except Exception:
        for tmp, _ in staged:
            tmp.unlink(missing_ok=True)
        raise

    written: dict[str, str] = {}
    for key, (tmp, target) in zip(format_keys, staged, strict=True):
        os.replace(tmp, target)
        written[key] = str(target)
    return written
