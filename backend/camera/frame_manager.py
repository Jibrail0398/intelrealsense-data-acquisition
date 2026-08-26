import logging
import threading
import time


logger = logging.getLogger(__name__)


class FrameBuffer:
    def __init__(self):
        self._lock = threading.Lock()
        self._rgb = None
        self._depth = None
        self._timestamp = 0.0

    def update(self, rgb, depth, timestamp=None):
        with self._lock:
            self._rgb = rgb
            self._depth = depth
            self._timestamp = timestamp if timestamp is not None else time.time()

    def clear(self):
        with self._lock:
            self._rgb = None
            self._depth = None
            self._timestamp = 0.0

    def get_latest(self):
        with self._lock:
            return self._rgb, self._depth, self._timestamp

    def has_frames(self):
        with self._lock:
            return self._rgb is not None and self._depth is not None
