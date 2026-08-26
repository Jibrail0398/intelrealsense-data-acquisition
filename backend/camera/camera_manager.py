import logging
import threading
import time

import numpy as np

from camera.camera_settings import (
    CameraSettings,
    DEFAULT_DEPTH_RESOLUTIONS,
    DEFAULT_FPS,
    DEFAULT_RGB_RESOLUTIONS,
)

logger = logging.getLogger(__name__)

STATE_DISCONNECTED = "disconnected"
STATE_CONNECTING = "connecting"
STATE_CONNECTED = "connected"
STATE_ERROR = "error"
STATE_RECONNECTING = "reconnecting"


class BaseCameraManager:
    def __init__(self, preview_config=None, on_status=None):
        self._preview_config = preview_config or {}
        self._on_status = on_status or (lambda status, device=None: None)
        self.settings = CameraSettings()
        self.state = STATE_DISCONNECTED
        self.device_info = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker = None
        self._depth_scale = 0.001

    def start(self):
        if self._worker and self._worker.is_alive():
            return
        self._stop_event.clear()
        self._worker = threading.Thread(target=self._run, daemon=True, name="camera-worker")
        self._worker.start()

    def stop(self):
        self._stop_event.set()
        if self._worker:
            self._worker.join(timeout=5)
        self._set_state(STATE_DISCONNECTED)

    def _set_state(self, state, device=None):
        with self._lock:
            self.state = state
            if device is not None:
                self.device_info = device
        logger.info("Camera status: %s", state)
        self._on_status(state, device)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                if not self._detect():
                    self._set_state(STATE_DISCONNECTED)
                    self._stop_event.wait(timeout=3)
                    continue
                self._set_state(STATE_CONNECTING)
                self._open_pipeline()
                self._set_state(STATE_CONNECTED, self._get_device_info())
                self._stream_loop()
            except Exception as exc:
                logger.error("Camera error: %s", exc)
                self._set_state(STATE_ERROR)
                self._safe_close()
                self._set_state(STATE_RECONNECTING)
                self._stop_event.wait(timeout=3)
            finally:
                self._safe_close()

    def connect(self):
        return self.get_status()

    def disconnect(self):
        self._safe_close()
        self._set_state(STATE_DISCONNECTED)
        return self.get_status()

    def get_status(self):
        with self._lock:
            return {
                "status": self.state,
                "device": self.device_info,
            }

    def get_capabilities(self):
        raise NotImplementedError

    def get_depth_scale(self):
        return self._depth_scale

    def get_settings(self):
        return self.settings.get()

    def update_settings(self, new_settings):
        caps = self.get_capabilities()
        valid, errors = self.settings.validate(new_settings, caps)
        if not valid:
            return False, errors
        needs_restart = any(
            k in new_settings for k in ("rgb_resolution", "depth_resolution", "fps")
        )
        self.settings.update(new_settings)
        if needs_restart and self.state == STATE_CONNECTED:
            self._restart_pipeline()
        return True, []

    def apply_advanced_controls(self):
        pass

    def _detect(self):
        raise NotImplementedError

    def _open_pipeline(self):
        raise NotImplementedError

    def _close_pipeline(self):
        raise NotImplementedError

    def _get_device_info(self):
        raise NotImplementedError

    def _read_frameset(self):
        raise NotImplementedError

    def _restart_pipeline(self):
        self._safe_close()

    def _safe_close(self):
        try:
            self._close_pipeline()
        except Exception:
            pass

    def _stream_loop(self):
        last_emit = 0.0
        min_interval = 1.0 / max(self._preview_config.get("target_fps", 15), 1)
        while not self._stop_event.is_set():
            rgb, depth, timestamp = self._read_frameset()
            if rgb is None or depth is None:
                continue
            self.frame_buffer.update(rgb, depth, timestamp)
            now = time.time()
            if now - last_emit >= min_interval:
                last_emit = now
                self.on_frame(rgb, depth, timestamp)


class MockCameraManager(BaseCameraManager):
    NAME = "Mock RealSense Camera"

    def __init__(self, preview_config, frame_buffer, on_frame, on_status=None):
        super().__init__(preview_config, on_status)
        self.frame_buffer = frame_buffer
        self.on_frame = on_frame
        self._frame_count = 0

    def _detect(self):
        time.sleep(0.2)
        return True

    def _open_pipeline(self):
        self._frame_count = 0
        self._depth_scale = 0.001
        logger.info("Mock pipeline started")

    def _close_pipeline(self):
        pass

    def _get_device_info(self):
        return {
            "name": self.NAME,
            "serial_number": "MOCK-000000",
            "firmware": "5.17.0",
            "mock": True,
        }

    def get_capabilities(self):
        return {
            "rgb_resolutions": DEFAULT_RGB_RESOLUTIONS[:6],
            "depth_resolutions": DEFAULT_DEPTH_RESOLUTIONS,
            "fps": [15, 30],
        }

    def _read_frameset(self):
        cfg = self.settings.get()
        w, h = cfg["rgb_resolution"]
        t = self._frame_count / max(cfg["fps"], 1)
        self._frame_count += 1

        x = np.linspace(0, 255, w, dtype=np.float32)
        y = np.linspace(0, 255, h, dtype=np.float32)
        gradient = (x[None, :] + y[:, None]) // 2
        cx = int((w / 2) * (1 + 0.5 * np.sin(t * 2 * np.pi)))
        cy = int(h / 2)
        yy, xx = np.mgrid[0:h, 0:w]
        dist2 = (xx - cx) ** 2 + (yy - cy) ** 2
        circle_mask = dist2 < (h // 4) ** 2
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        rgb[..., 0] = gradient.astype(np.uint8)
        rgb[..., 1] = (gradient * 0.8).astype(np.uint8)
        rgb[..., 2] = (gradient * 0.6).astype(np.uint8)
        rgb[circle_mask] = (60, 180, 75)

        dw, dh = cfg["depth_resolution"]
        dx = np.linspace(400, 2000, dw, dtype=np.uint16)
        depth = np.tile(dx, (dh, 1))
        dyy, dxx = np.mgrid[0:dh, 0:dw]
        dcx = int((dw / 2) * (1 + 0.5 * np.sin(t * 2 * np.pi)))
        dd = ((dxx - dcx) ** 2 + (dyy - dh // 2) ** 2) ** 0.5
        sphere = dd < dh // 3
        depth[sphere] = (600 + dd[sphere] * 4).astype(np.uint16)
        depth += np.random.randint(-10, 10, depth.shape).astype(np.uint16)

        time.sleep(1.0 / max(cfg["fps"], 1))
        return rgb, depth, time.time()


class RealCameraManager(BaseCameraManager):
    def __init__(self, preview_config, frame_buffer, on_frame, on_status=None):
        super().__init__(preview_config, on_status)
        import pyrealsense2 as rs

        self.rs = rs
        self.frame_buffer = frame_buffer
        self.on_frame = on_frame
        self.pipeline = None
        self.profile = None

    def _detect(self):
        ctx = self.rs.context()
        devices = list(ctx.query_devices())
        if not devices:
            return False
        return True

    def _open_pipeline(self):
        rs = self.rs
        cfg = self.settings.get()
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(
            rs.stream.color, cfg["rgb_resolution"][0], cfg["rgb_resolution"][1],
            rs.format.bgr8, cfg["fps"],
        )
        config.enable_stream(
            rs.stream.depth, cfg["depth_resolution"][0], cfg["depth_resolution"][1],
            rs.format.z16, cfg["fps"],
        )
        self.profile = self.pipeline.start(config)
        sensor = self.profile.get_device().first_depth_sensor()
        self._depth_scale = sensor.get_depth_scale()
        logger.info("RealSense pipeline started (depth_scale=%s)", self._depth_scale)
        self.apply_advanced_controls()

    def _close_pipeline(self):
        if self.pipeline:
            try:
                self.pipeline.stop()
            except Exception:
                pass
            self.pipeline = None
            self.profile = None
            logger.info("RealSense pipeline stopped")

    def _get_device_info(self):
        if not self.profile:
            return None
        device = self.profile.get_device()
        return {
            "name": device.get_info(self.rs.camera_info.name),
            "serial_number": device.get_info(self.rs.camera_info.serial_number),
            "firmware": device.get_info(self.rs.camera_info.firmware_version),
            "mock": False,
        }

    def get_capabilities(self):
        capabilities = {
            "rgb_resolutions": [],
            "depth_resolutions": [],
            "fps": [],
        }
        try:
            ctx = self.rs.context()
            for device in ctx.query_devices():
                for sensor in device.query_sensors():
                    profiles = sensor.get_stream_profiles()
                    seen_rgb = set()
                    seen_depth = set()
                    seen_fps = set()
                    for p in profiles:
                        if p.stream_type() != self.rs.stream.color and \
                                p.stream_type() != self.rs.stream.depth:
                            continue
                        vp = p.as_video_stream_profile()
                        key = (vp.width(), vp.height())
                        if p.stream_type() == self.rs.stream.color:
                            if key not in seen_rgb:
                                seen_rgb.add(key)
                                capabilities["rgb_resolutions"].append(list(key))
                        else:
                            if key not in seen_depth:
                                seen_depth.add(key)
                                capabilities["depth_resolutions"].append(list(key))
                        if p.fps() not in seen_fps:
                            seen_fps.add(p.fps())
                            capabilities["fps"].append(p.fps())
        except Exception as exc:
            logger.warning("Failed to query capabilities: %s", exc)
            capabilities = {
                "rgb_resolutions": DEFAULT_RGB_RESOLUTIONS,
                "depth_resolutions": DEFAULT_DEPTH_RESOLUTIONS,
                "fps": DEFAULT_FPS,
            }
        capabilities["fps"] = sorted(set(capabilities["fps"]))
        return capabilities

    def apply_advanced_controls(self):
        if not self.profile:
            return
        cfg = self.settings.get()
        color_sensor = self.profile.get_device().query_sensors()[1]
        try:
            if cfg["exposure"] == "auto":
                color_sensor.set_option(self.rs.option.enable_auto_exposure, 1.0)
            else:
                color_sensor.set_option(self.rs.option.enable_auto_exposure, 0.0)
                color_sensor.set_option(self.rs.option.exposure, float(cfg["exposure"]))
            if cfg["white_balance"] != "auto":
                color_sensor.set_option(self.rs.option.white_balance, float(cfg["white_balance"]))
        except Exception as exc:
            logger.warning("Advanced controls not applied: %s", exc)

    def _read_frameset(self):
        frames = self.pipeline.wait_for_frames(timeout_ms=5000)
        align = self.rs.align(self.rs.stream.color)
        frames = align.process(frames)
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()
        if not color or not depth:
            return None, None, None
        rgb = np.asanyarray(color.get_data())
        depth_data = np.asanyarray(depth.get_data())
        return rgb, depth_data, frames.get_timestamp() / 1000.0


def create_camera_manager(app_config, frame_buffer, on_frame, on_status=None):
    preview_cfg = app_config.preview
    if app_config.mock_camera:
        return MockCameraManager(preview_cfg, frame_buffer, on_frame, on_status)
    return RealCameraManager(preview_cfg, frame_buffer, on_frame, on_status)
