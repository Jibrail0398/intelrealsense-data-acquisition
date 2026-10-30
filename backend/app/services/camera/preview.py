"""Turning raw frames into JPEG previews for the browser."""

import cv2
import numpy as np

from app.schemas.camera import PreviewConfig

_COLORMAPS = {
    "turbo": cv2.COLORMAP_TURBO,
    "jet": cv2.COLORMAP_JET,
    "inferno": cv2.COLORMAP_INFERNO,
    "viridis": cv2.COLORMAP_VIRIDIS,
    "bone": cv2.COLORMAP_BONE,
}


def colorize_depth(depth: np.ndarray, depth_scale: float, preview: PreviewConfig) -> np.ndarray:
    metres = depth.astype(np.float32) * depth_scale
    span = max(preview.max_distance - preview.min_distance, 1e-3)
    norm = np.clip((metres - preview.min_distance) / span, 0, 1)
    coloured = cv2.applyColorMap((norm * 255).astype(np.uint8), _COLORMAPS[preview.colormap])
    coloured[depth == 0] = 0  # no data stays black
    return coloured


def encode_jpeg(image: np.ndarray, quality: int) -> bytes:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("Could not encode preview")
    return buf.tobytes()
