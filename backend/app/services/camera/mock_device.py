"""A simulated RGB-D camera, for running the app without RealSense hardware.

Enable with ``CAMERA_BACKEND=mock``. It never runs unless asked for, so a
dataset can never silently fill with synthetic frames.
"""

import time
from dataclasses import dataclass

import cv2
import numpy as np

from app.schemas.camera import (
    CameraConfig,
    FilterConfig,
    OptionChoice,
    SensorOption,
    SensorOptions,
    StreamCapabilities,
)
from app.services.camera.base import CameraDevice, RawFrames, group_profiles, humanize

_RESOLUTIONS = [(1280, 720), (848, 480), (640, 480), (640, 360), (480, 270), (424, 240)]
_RATES = [6, 15, 30]


@dataclass
class _Opt:
    name: str
    min: float
    max: float
    step: float
    default: float
    description: str
    choices: dict[int, str] | None = None
    read_only: bool = False


_SENSORS: dict[str, tuple[str, list[_Opt]]] = {
    "stereo_module": ("Stereo Module", [
        _Opt("visual_preset", 0, 5, 1, 1, "Advanced-mode preset for the depth algorithm",
             {0: "Custom", 1: "Default", 2: "Hand", 3: "High Accuracy", 4: "High Density", 5: "Medium Density"}),
        _Opt("enable_auto_exposure", 0, 1, 1, 1, "Enable auto exposure"),
        _Opt("exposure", 1, 165000, 1, 8500, "Depth exposure in microseconds"),
        _Opt("gain", 16, 248, 1, 16, "UVC image gain"),
        _Opt("emitter_enabled", 0, 2, 1, 1, "Power of the IR projector",
             {0: "Off", 1: "Laser", 2: "Laser Auto"}),
        _Opt("laser_power", 0, 360, 30, 150, "Manual laser power in mW"),
        _Opt("depth_units", 0.0001, 0.01, 0.000001, 0.001, "Number of metres represented by a single depth unit"),
        _Opt("asic_temperature", -40, 125, 0, 38, "Current ASIC temperature in °C", read_only=True),
    ]),
    "rgb_camera": ("RGB Camera", [
        _Opt("enable_auto_exposure", 0, 1, 1, 1, "Enable auto exposure"),
        _Opt("exposure", 1, 10000, 1, 156, "Controls exposure time of colour camera"),
        _Opt("gain", 0, 128, 1, 64, "UVC image gain"),
        _Opt("brightness", -64, 64, 1, 0, "UVC image brightness"),
        _Opt("contrast", 0, 100, 1, 50, "UVC image contrast"),
        _Opt("gamma", 100, 500, 1, 300, "UVC image gamma"),
        _Opt("hue", -180, 180, 1, 0, "UVC image hue"),
        _Opt("saturation", 0, 100, 1, 64, "UVC image saturation"),
        _Opt("sharpness", 0, 100, 1, 50, "UVC image sharpness"),
        _Opt("enable_auto_white_balance", 0, 1, 1, 1, "Enable auto white balance"),
        _Opt("white_balance", 2800, 6500, 10, 4600, "White balance in Kelvin"),
        _Opt("backlight_compensation", 0, 1, 1, 0, "Enable backlight compensation"),
        _Opt("power_line_frequency", 0, 3, 1, 3, "Power line frequency, to cancel flicker",
             {0: "Disabled", 1: "50Hz", 2: "60Hz", 3: "Auto"}),
        _Opt("auto_exposure_priority", 0, 1, 1, 0, "Allow the frame rate to drop to keep exposure"),
    ]),
}


class MockDevice(CameraDevice):
    backend = "mock"

    def __init__(self) -> None:
        self._open = False
        self._values = {
            key: {o.name: o.default for o in opts} for key, (_, opts) in _SENSORS.items()
        }
        self._started = 0.0
        self._last = 0.0
        self._threshold: tuple[float, float] | None = None

    def is_available(self) -> bool:
        return True

    def open(self, config: CameraConfig) -> None:
        self.warning = None
        self.active_color = config.color
        self.active_depth = config.depth
        self.depth_scale = self._values["stereo_module"]["depth_units"]
        self._align = config.align_to_color
        self.set_processing(config.align_to_color, config.filters)
        self._open = True
        self._started = self._last = time.monotonic()

    def close(self) -> None:
        self._open = False

    def read(self, timeout_ms: int = 1000) -> RawFrames | None:
        if not self._open or self.active_color is None or self.active_depth is None:
            raise RuntimeError("Pipeline is not running")
        period = 1.0 / self.active_color.fps
        wait = self._last + period - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()
        t = self._last - self._started

        cw, ch = self.active_color.width, self.active_color.height
        dw, dh = (cw, ch) if self._align else (self.active_depth.width, self.active_depth.height)
        return RawFrames(
            color=self._color(cw, ch, t),
            depth=self._depth(dw, dh, t),
            intrinsics={"width": dw, "height": dh, "fx": dw * 0.95, "fy": dw * 0.95,
                        "ppx": dw / 2, "ppy": dh / 2, "model": "mock", "coeffs": [0, 0, 0, 0, 0]},
        )

    def set_processing(self, align_to_color: bool, filters: FilterConfig) -> None:
        self._align = align_to_color
        t = filters.threshold
        self._threshold = (t.min_distance, t.max_distance) if t.enabled else None

    def info(self) -> dict[str, str]:
        return {
            "name": "Simulated RealSense D435",
            "serial_number": "MOCK-000000",
            "firmware_version": "5.16.0.1",
            "usb_type": "3.2",
            "product_line": "D400",
        }

    def capabilities(self) -> StreamCapabilities:
        profiles = {(w, h, f) for w, h in _RESOLUTIONS for f in _RATES}
        return StreamCapabilities(color=group_profiles(profiles), depth=group_profiles(profiles))

    def sensor_options(self) -> list[SensorOptions]:
        result = []
        for key, (name, opts) in _SENSORS.items():
            options = []
            for o in opts:
                kind = "bool" if (o.min, o.max, o.step) == (0, 1, 1) else "choice" if o.choices else "range"
                options.append(SensorOption(
                    name=o.name, label=humanize(o.name), description=o.description,
                    value=self._values[key][o.name], min=o.min, max=o.max, step=o.step,
                    default=o.default, read_only=o.read_only, kind=kind,
                    choices=[OptionChoice(value=v, label=lbl) for v, lbl in o.choices.items()] if o.choices else None,
                ))
            result.append(SensorOptions(key=key, name=name, options=options))
        return result

    def set_option(self, sensor_key: str, option: str, value: float) -> None:
        if sensor_key not in _SENSORS:
            raise ValueError(f"Unknown sensor {sensor_key}")
        spec = next((o for o in _SENSORS[sensor_key][1] if o.name == option), None)
        if spec is None:
            raise ValueError(f"{option} is not supported by this sensor")
        if spec.read_only:
            raise ValueError(f"{option} is read-only")
        if not (spec.min <= value <= spec.max):
            raise ValueError(f"{option} must be between {spec.min:g} and {spec.max:g}")
        values = self._values[sensor_key]
        values[option] = value
        # Mirror librealsense: a manual exposure turns auto exposure off.
        if option == "exposure":
            values["enable_auto_exposure"] = 0
        if option == "white_balance":
            values["enable_auto_white_balance"] = 0
        if option == "depth_units":
            self.depth_scale = value

    def hardware_reset(self) -> None:
        for key, (_, opts) in _SENSORS.items():
            self._values[key] = {o.name: o.default for o in opts}

    # -- synthetic scene ---------------------------------------------------

    def _color(self, w: int, h: int, t: float) -> np.ndarray:
        rgb = self._values["rgb_camera"]
        img = np.full((h, w, 3), (64, 70, 74), np.uint8)
        cv2.rectangle(img, (0, int(h * 0.72)), (w, h), (92, 98, 104), -1)
        cx = int(w * (0.5 + 0.18 * np.sin(t * 0.6)))
        cv2.ellipse(img, (cx, int(h * 0.42)), (int(w * 0.09), int(h * 0.30)), 0, 0, 360, (150, 170, 200), -1)
        cv2.circle(img, (cx, int(h * 0.14)), int(h * 0.07), (160, 180, 210), -1)
        scale = h / 480
        cv2.putText(img, "SIMULATED CAMERA", (int(16 * scale), int(36 * scale)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8 * scale, (235, 235, 235), max(1, int(2 * scale)))
        cv2.putText(img, time.strftime("%H:%M:%S"), (int(16 * scale), int(68 * scale)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6 * scale, (200, 200, 200), max(1, int(scale)))
        gain = 1.0
        if not rgb["enable_auto_exposure"]:
            gain = float(np.clip(rgb["exposure"] / 156, 0.2, 3.0))
        out = img.astype(np.float32) * gain * (rgb["contrast"] / 50) + rgb["brightness"] * 1.5
        return np.clip(out, 0, 255).astype(np.uint8)

    def _depth(self, w: int, h: int, t: float) -> np.ndarray:
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        metres = np.full((h, w), 2.6, np.float32)
        floor = ys > h * 0.72
        metres[floor] = 2.6 - (ys[floor] - h * 0.72) / (h * 0.28) * 1.6
        cx = w * (0.5 + 0.18 * np.sin(t * 0.6))
        body = ((xs - cx) / (w * 0.09)) ** 2 + ((ys - h * 0.42) / (h * 0.30)) ** 2 <= 1
        head = ((xs - cx) ** 2 + (ys - h * 0.14) ** 2) <= (h * 0.07) ** 2
        metres[body | head] = 1.2
        noise = np.random.default_rng().normal(0, 0.004, (h, w)).astype(np.float32)
        metres += noise
        metres[(xs < w * 0.04)] = 0  # the left-edge shadow every stereo camera has
        if self._threshold:
            lo, hi = self._threshold
            metres[(metres < lo) | (metres > hi)] = 0
        return np.clip(metres / self.depth_scale, 0, 65535).astype(np.uint16)
