"""Intel RealSense camera over USB, through pyrealsense2."""

import logging

import numpy as np

from app.schemas.camera import (
    CameraConfig,
    FilterConfig,
    OptionChoice,
    SensorOption,
    SensorOptions,
    StreamCapabilities,
    StreamProfile,
)
from app.services.camera.base import CameraDevice, RawFrames, group_profiles, humanize, sensor_key

log = logging.getLogger(__name__)

# Options whose numeric range is small enough to list every value with its description.
_MAX_CHOICES = 24


class RealSenseDevice(CameraDevice):
    backend = "realsense"

    def __init__(self) -> None:
        import pyrealsense2 as rs  # imported lazily so mock mode works without it

        self.rs = rs
        self._ctx = rs.context()
        self._pipeline = None
        self._device = None
        self._align = None
        self._filters: tuple = ()

    # -- lifecycle ---------------------------------------------------------

    def is_available(self) -> bool:
        return len(self._ctx.query_devices()) > 0

    def open(self, config: CameraConfig) -> None:
        rs = self.rs
        self.warning = None
        pipeline = rs.pipeline(self._ctx)
        cfg = rs.config()
        cfg.enable_stream(rs.stream.color, config.color.width, config.color.height,
                          rs.format.bgr8, config.color.fps)
        cfg.enable_stream(rs.stream.depth, config.depth.width, config.depth.height,
                          rs.format.z16, config.depth.fps)
        try:
            profile = pipeline.start(cfg)
        except RuntimeError as exc:
            log.warning("Requested stream profile rejected (%s); using device defaults", exc)
            self.warning = "The saved resolution is not supported by this camera; using its defaults."
            cfg = rs.config()
            cfg.enable_stream(rs.stream.color, rs.format.bgr8, 30)
            cfg.enable_stream(rs.stream.depth, rs.format.z16, 30)
            profile = pipeline.start(cfg)

        self._pipeline = pipeline
        self._device = profile.get_device()
        self.depth_scale = float(self._device.first_depth_sensor().get_depth_scale())
        self.active_color = self._profile_of(profile.get_stream(rs.stream.color))
        self.active_depth = self._profile_of(profile.get_stream(rs.stream.depth))
        self.set_processing(config.align_to_color, config.filters)

    def close(self) -> None:
        if self._pipeline is not None:
            try:
                self._pipeline.stop()
            except RuntimeError:
                pass
        self._pipeline = None
        self._device = None
        self.active_color = self.active_depth = None

    def read(self, timeout_ms: int = 1000) -> RawFrames | None:
        if self._pipeline is None:
            raise RuntimeError("Pipeline is not running")
        frames = self._pipeline.wait_for_frames(timeout_ms)
        align, filters = self._align, self._filters
        if align is not None:
            frames = align.process(frames)
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()
        if not color or not depth:
            return None
        for block in filters:
            depth = block.process(depth)
        depth = depth.as_depth_frame()
        return RawFrames(
            color=np.asanyarray(color.get_data()).copy(),
            depth=np.asanyarray(depth.get_data()).copy(),
            intrinsics=self._intrinsics(depth),
        )

    def set_processing(self, align_to_color: bool, filters: FilterConfig) -> None:
        rs = self.rs
        self._align = rs.align(rs.stream.color) if align_to_color else None
        self._filters = tuple(self._build_filters(filters))

    def hardware_reset(self) -> None:
        device = self._device or next(iter(self._ctx.query_devices()), None)
        if device is None:
            raise RuntimeError("No RealSense camera detected")
        device.hardware_reset()

    # -- description -------------------------------------------------------

    def info(self) -> dict[str, str]:
        rs = self.rs
        device = self._device or next(iter(self._ctx.query_devices()), None)
        if device is None:
            return {}
        fields = {
            "name": rs.camera_info.name,
            "serial_number": rs.camera_info.serial_number,
            "firmware_version": rs.camera_info.firmware_version,
            "recommended_firmware_version": rs.camera_info.recommended_firmware_version,
            "usb_type": rs.camera_info.usb_type_descriptor,
            "product_line": rs.camera_info.product_line,
            "product_id": rs.camera_info.product_id,
        }
        return {key: device.get_info(info) for key, info in fields.items() if device.supports(info)}

    def capabilities(self) -> StreamCapabilities:
        rs = self.rs
        device = self._device or next(iter(self._ctx.query_devices()), None)
        color: set[tuple[int, int, int]] = set()
        depth: set[tuple[int, int, int]] = set()
        if device is not None:
            for sensor in device.query_sensors():
                for p in sensor.get_stream_profiles():
                    if not p.is_video_stream_profile():
                        continue
                    v = p.as_video_stream_profile()
                    entry = (v.width(), v.height(), p.fps())
                    if p.stream_type() == rs.stream.color and p.format() == rs.format.bgr8:
                        color.add(entry)
                    elif p.stream_type() == rs.stream.depth and p.format() == rs.format.z16:
                        depth.add(entry)
        return StreamCapabilities(color=group_profiles(color), depth=group_profiles(depth))

    def sensor_options(self) -> list[SensorOptions]:
        device = self._device or next(iter(self._ctx.query_devices()), None)
        if device is None:
            return []
        result = []
        for sensor in device.query_sensors():
            name = sensor.get_info(self.rs.camera_info.name)
            options = [o for o in (self._describe(sensor, opt) for opt in self._supported(sensor)) if o]
            if options:
                result.append(SensorOptions(key=sensor_key(name), name=name, options=options))
        return result

    def set_option(self, sensor_key_: str, option: str, value: float) -> None:
        sensor = self._find_sensor(sensor_key_)
        opt = self.rs.option.__members__.get(option)
        if opt is None or not sensor.supports(opt):
            raise ValueError(f"{option} is not supported by this sensor")
        if sensor.is_option_read_only(opt):
            raise ValueError(f"{option} is read-only")
        rng = sensor.get_option_range(opt)
        if not (rng.min <= value <= rng.max):
            raise ValueError(f"{option} must be between {rng.min:g} and {rng.max:g}")
        sensor.set_option(opt, float(value))

    # -- helpers -----------------------------------------------------------

    def _supported(self, sensor) -> list:
        items = sensor.get_supported_options()
        # 2.56+ may return option_value objects; older versions return the enum.
        return [getattr(item, "id", item) for item in items]

    def _describe(self, sensor, opt) -> SensorOption | None:
        try:
            rng = sensor.get_option_range(opt)
            value = float(sensor.get_option(opt))
            read_only = bool(sensor.is_option_read_only(opt))
            description = sensor.get_option_description(opt) or ""
        except (RuntimeError, TypeError):
            return None  # string or composite options cannot be shown as a number

        name = getattr(opt, "name", str(opt).split(".")[-1])
        kind = "range"
        choices = None
        if rng.min == 0 and rng.max == 1 and rng.step == 1:
            kind = "bool"
        elif rng.step >= 1 and 0 < (rng.max - rng.min) / rng.step <= _MAX_CHOICES:
            labels = []
            v = rng.min
            while v <= rng.max + 1e-9:
                label = sensor.get_option_value_description(opt, v)
                labels.append(OptionChoice(value=v, label=label) if label else None)
                v += rng.step
            if labels and all(labels):
                kind = "choice"
                choices = labels  # type: ignore[assignment]

        return SensorOption(
            name=name, label=humanize(name), description=description, value=value,
            min=rng.min, max=rng.max, step=rng.step, default=rng.default,
            read_only=read_only, kind=kind, choices=choices,
        )

    def _find_sensor(self, key: str):
        device = self._device or next(iter(self._ctx.query_devices()), None)
        if device is None:
            raise RuntimeError("No RealSense camera detected")
        for sensor in device.query_sensors():
            if sensor_key(sensor.get_info(self.rs.camera_info.name)) == key:
                return sensor
        raise ValueError(f"Unknown sensor {key}")

    def _build_filters(self, f: FilterConfig) -> list:
        rs = self.rs
        o = rs.option
        blocks = []
        if f.decimation.enabled:
            block = rs.decimation_filter()
            block.set_option(o.filter_magnitude, f.decimation.magnitude)
            blocks.append(block)
        if f.threshold.enabled:
            block = rs.threshold_filter()
            block.set_option(o.min_distance, f.threshold.min_distance)
            block.set_option(o.max_distance, f.threshold.max_distance)
            blocks.append(block)
        use_disparity = f.disparity_domain and (f.spatial.enabled or f.temporal.enabled)
        if use_disparity:
            blocks.append(rs.disparity_transform(True))
        if f.spatial.enabled:
            block = rs.spatial_filter()
            block.set_option(o.filter_magnitude, f.spatial.magnitude)
            block.set_option(o.filter_smooth_alpha, f.spatial.smooth_alpha)
            block.set_option(o.filter_smooth_delta, f.spatial.smooth_delta)
            block.set_option(o.holes_fill, f.spatial.holes_fill)
            blocks.append(block)
        if f.temporal.enabled:
            block = rs.temporal_filter()
            block.set_option(o.filter_smooth_alpha, f.temporal.smooth_alpha)
            block.set_option(o.filter_smooth_delta, f.temporal.smooth_delta)
            block.set_option(o.holes_fill, f.temporal.persistence)
            blocks.append(block)
        if use_disparity:
            blocks.append(rs.disparity_transform(False))
        if f.hole_filling.enabled:
            block = rs.hole_filling_filter()
            block.set_option(o.holes_fill, f.hole_filling.mode)
            blocks.append(block)
        return blocks

    @staticmethod
    def _profile_of(stream_profile) -> StreamProfile:
        v = stream_profile.as_video_stream_profile()
        return StreamProfile(width=v.width(), height=v.height(), fps=stream_profile.fps())

    @staticmethod
    def _intrinsics(frame) -> dict:
        i = frame.profile.as_video_stream_profile().get_intrinsics()
        return {
            "width": i.width, "height": i.height, "fx": i.fx, "fy": i.fy,
            "ppx": i.ppx, "ppy": i.ppy, "model": str(i.model), "coeffs": list(i.coeffs),
        }
