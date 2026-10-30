"""Owns the one camera pipeline for the whole app.

A single background thread opens the device, reads synchronised framesets and
keeps the latest one in memory. HTTP requests never open or close the pipeline
themselves; they read the latest frame or ask the thread to reconnect.
The thread also polls USB, so plugging the camera in connects it automatically.
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from app.core.config import Settings
from app.core.exceptions import CameraNotReadyError
from app.schemas.camera import CameraConfig, CameraStatus, CameraStatusValue
from app.services.camera.base import CameraDevice
from app.services.camera.preview import colorize_depth, encode_jpeg
from app.services.event_hub import EventHub

log = logging.getLogger(__name__)

_MAX_READ_FAILURES = 3


@dataclass
class FrameBundle:
    seq: int
    timestamp: float
    color: np.ndarray
    depth: np.ndarray
    depth_scale: float
    intrinsics: dict = field(default_factory=dict)


def create_device(settings: Settings) -> CameraDevice:
    if settings.camera_backend == "mock":
        from app.services.camera.mock_device import MockDevice

        return MockDevice()
    from app.services.camera.realsense_device import RealSenseDevice

    return RealSenseDevice()


class CameraManager:
    def __init__(self, settings: Settings, hub: EventHub, config: CameraConfig) -> None:
        self._settings = settings
        self._hub = hub
        self._config = config
        self._device: CameraDevice | None = None
        self._device_error: str | None = None
        self._open = False

        self._status: CameraStatusValue = "disconnected"
        self._message: str | None = None
        self._want_connected = settings.camera_auto_connect
        self._restart = False

        self._latest: FrameBundle | None = None
        self._seq = 0
        self._frame_times: deque[float] = deque(maxlen=30)
        self._frame_cond = threading.Condition()
        self._preview_cache: dict[str, tuple[int, bytes]] = {}

        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._device_lock = threading.RLock()

    # -- public API --------------------------------------------------------

    @property
    def backend(self) -> str:
        return "mock" if self._settings.camera_backend == "mock" else "realsense"

    @property
    def config(self) -> CameraConfig:
        return self._config

    @property
    def device(self) -> CameraDevice | None:
        return self._device

    @property
    def is_connected(self) -> bool:
        return self._status == "connected"

    def start(self) -> None:
        try:
            self._device = create_device(self._settings)
        except ImportError:
            self._device_error = "pyrealsense2 is not installed in the backend environment."
            self._set_status("error", self._device_error)
            return
        self._thread = threading.Thread(target=self._run, name="camera", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._close_device()

    def connect(self) -> None:
        self._want_connected = True
        self._wake.set()

    def disconnect(self) -> None:
        self._want_connected = False
        self._wake.set()

    def restart(self) -> None:
        self._restart = True
        self._wake.set()

    def status(self) -> CameraStatus:
        device = self._device
        connected = self._status == "connected" and device is not None
        times = list(self._frame_times)
        fps = (len(times) - 1) / (times[-1] - times[0]) if len(times) > 1 and times[-1] > times[0] else 0.0
        info = None
        if connected:
            try:
                info = device.info()
            except RuntimeError:
                info = None
        return CameraStatus(
            status=self._status,
            message=self._message,
            backend=self.backend,  # type: ignore[arg-type]
            device=info,
            color=device.active_color if connected else None,
            depth=device.active_depth if connected else None,
            fps=round(fps, 1) if connected else 0.0,
        )

    def update_config(self, config: CameraConfig, *, restart_stream: bool) -> None:
        self._config = config
        self._preview_cache.clear()
        if restart_stream:
            self.restart()
        elif self._device is not None and self._open:
            with self._device_lock:
                self._device.set_processing(config.align_to_color, config.filters)

    def require_device(self) -> CameraDevice:
        if self._device is None:
            raise CameraNotReadyError(self._device_error or "Camera backend is not available")
        return self._device

    def require_connected(self) -> CameraDevice:
        device = self.require_device()
        if not self.is_connected:
            raise CameraNotReadyError(self._message or "Camera is not connected")
        return device

    def latest(self) -> FrameBundle | None:
        return self._latest

    def wait_for_frame(self, after_seq: int, timeout: float = 3.0) -> FrameBundle:
        """Block until a frameset newer than ``after_seq`` arrives."""
        deadline = time.monotonic() + timeout
        with self._frame_cond:
            while self._latest is None or self._latest.seq <= after_seq:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not self.is_connected:
                    raise CameraNotReadyError("Camera did not deliver a new frame in time")
                self._frame_cond.wait(remaining)
            return self._latest

    def preview_jpeg(self, kind: str) -> tuple[int, bytes] | None:
        frame = self._latest
        if frame is None or not self.is_connected:
            return None
        cached = self._preview_cache.get(kind)
        if cached and cached[0] == frame.seq:
            return cached
        if kind == "depth":
            image = colorize_depth(frame.depth, frame.depth_scale, self._config.preview)
        else:
            image = frame.color
        entry = (frame.seq, encode_jpeg(image, self._settings.preview_jpeg_quality))
        self._preview_cache[kind] = entry
        return entry

    def hardware_reset(self) -> None:
        device = self.require_device()
        with self._device_lock:
            device.hardware_reset()
        self._close_device()
        self._set_status("connecting", "Resetting camera…")
        self._wake.set()

    # -- worker ------------------------------------------------------------

    def _run(self) -> None:
        failures = 0
        while not self._stop.is_set():
            if not self._want_connected:
                if self._open:
                    self._close_device()
                self._set_status("disconnected", "Disconnected by user")
                self._sleep(1.0)
                continue

            if self._restart and self._open:
                self._close_device()
            self._restart = False

            if not self._open:
                if not self._try_open():
                    self._sleep(self._settings.camera_poll_seconds)
                continue

            try:
                with self._device_lock:
                    raw = self._device.read(1000) if self._device else None
            except Exception as exc:  # timeout, unplugged, USB error
                failures += 1
                log.warning("Frame read failed (%d/%d): %s", failures, _MAX_READ_FAILURES, exc)
                if failures >= _MAX_READ_FAILURES:
                    failures = 0
                    self._close_device()
                    self._set_status("disconnected", "Camera stopped sending frames. Check the USB cable.")
                continue
            failures = 0
            if raw is None:
                continue
            now = time.monotonic()
            self._frame_times.append(now)
            with self._frame_cond:
                self._seq += 1
                self._latest = FrameBundle(
                    seq=self._seq, timestamp=time.time(), color=raw.color, depth=raw.depth,
                    depth_scale=self._device.depth_scale if self._device else 0.001,
                    intrinsics=raw.intrinsics,
                )
                self._frame_cond.notify_all()

    def _try_open(self) -> bool:
        device = self._device
        if device is None:
            return False
        try:
            if not device.is_available():
                self._set_status("disconnected", "No RealSense camera detected on USB")
                return False
            self._set_status("connecting", "Starting camera streams…")
            with self._device_lock:
                device.open(self._config)
                self._apply_saved_options(device)
            self._open = True
            self._frame_times.clear()
            self._set_status("connected", device.warning)
            return True
        except Exception as exc:
            log.exception("Could not open camera")
            self._close_device()
            self._set_status("error", f"Could not start the camera: {exc}")
            return False

    def _apply_saved_options(self, device: CameraDevice) -> None:
        for sensor, values in self._config.options.items():
            for option, value in values.items():
                try:
                    device.set_option(sensor, option, value)
                except Exception as exc:
                    log.info("Skipped saved option %s.%s: %s", sensor, option, exc)

    def _close_device(self) -> None:
        with self._device_lock:
            if self._device is not None and self._open:
                self._device.close()
            self._open = False
        self._latest = None
        self._preview_cache.clear()
        with self._frame_cond:
            self._frame_cond.notify_all()

    def _sleep(self, seconds: float) -> None:
        self._wake.wait(seconds)
        self._wake.clear()

    def _set_status(self, status: CameraStatusValue, message: str | None) -> None:
        if status == self._status and message == self._message:
            return
        self._status, self._message = status, message
        log.info("Camera %s%s", status, f": {message}" if message else "")
        self._hub.publish_threadsafe("camera.status", self.status())
