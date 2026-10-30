"""The interface every camera backend (RealSense or mock) implements."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from app.schemas.camera import (
    CameraConfig,
    FilterConfig,
    ResolutionOption,
    SensorOptions,
    StreamCapabilities,
    StreamProfile,
)


@dataclass
class RawFrames:
    color: np.ndarray  # HxWx3 uint8, BGR
    depth: np.ndarray  # HxW uint16, raw depth units (multiply by depth_scale for metres)
    intrinsics: dict = field(default_factory=dict)


class CameraDevice(ABC):
    backend: str

    depth_scale: float = 0.001
    active_color: StreamProfile | None = None
    active_depth: StreamProfile | None = None
    warning: str | None = None

    @abstractmethod
    def is_available(self) -> bool:
        """True when a device is plugged in and can be opened."""

    @abstractmethod
    def open(self, config: CameraConfig) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def read(self, timeout_ms: int = 1000) -> RawFrames | None:
        """Block until the next synchronised frameset. Raises RuntimeError on failure."""

    @abstractmethod
    def set_processing(self, align_to_color: bool, filters: FilterConfig) -> None:
        """Swap alignment and post-processing without restarting the stream."""

    @abstractmethod
    def info(self) -> dict[str, str]: ...

    @abstractmethod
    def capabilities(self) -> StreamCapabilities: ...

    @abstractmethod
    def sensor_options(self) -> list[SensorOptions]: ...

    @abstractmethod
    def set_option(self, sensor_key: str, option: str, value: float) -> None: ...

    @abstractmethod
    def hardware_reset(self) -> None: ...


def group_profiles(profiles: set[tuple[int, int, int]]) -> list[ResolutionOption]:
    """{(w, h, fps)} -> resolutions sorted largest first, each with its frame rates."""
    by_res: dict[tuple[int, int], set[int]] = {}
    for w, h, fps in profiles:
        by_res.setdefault((w, h), set()).add(fps)
    return [
        ResolutionOption(width=w, height=h, fps=sorted(rates))
        for (w, h), rates in sorted(by_res.items(), key=lambda kv: (-kv[0][0] * kv[0][1], -kv[0][0]))
    ]


def sensor_key(name: str) -> str:
    return "_".join(name.lower().split())


def humanize(option_name: str) -> str:
    text = option_name.replace("_", " ").strip()
    return text[:1].upper() + text[1:]
