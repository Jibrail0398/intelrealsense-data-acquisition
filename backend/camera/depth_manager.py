import logging


logger = logging.getLogger(__name__)


class DepthManager:
    def __init__(self, frame_buffer, camera_manager):
        self._buffer = frame_buffer
        self._camera = camera_manager

    @property
    def depth_scale(self):
        scale = self._camera.get_depth_scale()
        return scale if scale else 0.001

    def query(self, x, y):
        _, depth, _ = self._buffer.get_latest()
        if depth is None:
            return {"x": x, "y": y, "depth_raw": None, "depth_scale": self.depth_scale,
                    "distance_m": None, "valid": False}
        h, w = depth.shape[:2]
        xi, yi = int(x), int(y)
        if xi < 0 or yi < 0 or xi >= w or yi >= h:
            return {"x": x, "y": y, "depth_raw": None, "depth_scale": self.depth_scale,
                    "distance_m": None, "valid": False}
        raw = int(depth[yi, xi])
        valid = raw > 0
        distance = raw * self.depth_scale if valid else None
        return {
            "x": xi,
            "y": yi,
            "depth_raw": raw,
            "depth_scale": self.depth_scale,
            "distance_m": round(distance, 4) if distance is not None else None,
            "valid": valid,
        }
