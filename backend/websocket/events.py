import base64
import logging

import cv2


logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, socketio):
        self.socketio = socketio

    def emit(self, event, payload):
        try:
            self.socketio.emit(event, payload)
        except Exception as exc:
            logger.error("WebSocket emit failed (%s): %s", event, exc)

    def camera_status(self, status, device=None):
        self.emit("camera.status", {"event": "camera.status", "status": status,
                                    "device": device})

    def camera_frame(self, rgb, depth, timestamp, quality=70):
        ok_rgb, buf_rgb = cv2.imencode(".jpg", rgb,
                                       [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
        ok_depth, buf_depth = cv2.imencode(".jpg", depth,
                                           [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
        if not (ok_rgb and ok_depth):
            return
        self.emit("camera.frame", {
            "event": "camera.frame",
            "rgb": "data:image/jpeg;base64," + base64.b64encode(buf_rgb).decode("ascii"),
            "depth": "data:image/jpeg;base64," + base64.b64encode(buf_depth).decode("ascii"),
            "timestamp": timestamp,
        })

    def storage_updated(self, info):
        info = dict(info)
        info["event"] = "storage.updated"
        self.emit("storage.updated", info)

    def dataset_updated(self, data):
        data = dict(data)
        data["event"] = "dataset.updated"
        self.emit("dataset.updated", data)

    def settings_changed(self, settings):
        settings = dict(settings)
        settings["event"] = "camera.settings.changed"
        self.emit("camera.settings.changed", settings)

    def error(self, code, message):
        self.emit("error", {"event": "error", "code": code, "message": message})
