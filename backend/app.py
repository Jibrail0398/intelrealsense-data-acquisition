import logging
import os
import signal
import sys
import threading

from flask import Flask, jsonify
from flask_socketio import SocketIO

from camera.camera_manager import create_camera_manager
from camera.depth_manager import DepthManager
from camera.frame_manager import FrameBuffer
from capture.capture_manager import CaptureManager
from config import BASE_DIR, config as app_config
from dataset.dataset_manager import DatasetManager
from dataset.metadata_manager import MetadataManager
from dataset.statistics import Statistics
from storage.storage_manager import StorageManager
from websocket.events import EventPublisher

sys.path.insert(0, BASE_DIR)


class Context:
    pass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
publisher = EventPublisher(socketio)
frame_buffer = FrameBuffer()
ctx = Context()


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    ctx.config = app_config
    ctx.publisher = publisher
    ctx.frame_buffer = frame_buffer

    if not app_config.storage_path:
        raise RuntimeError("storage_path is not configured")
    storage = StorageManager(app_config)
    storage.ensure_root()

    metadata = MetadataManager(storage)
    datasets = DatasetManager(storage, metadata)
    stats = Statistics(storage, metadata)

    def on_camera_frame(rgb, depth, timestamp):
        preview_quality = app_config.preview.get("jpeg_quality", 70)
        depth_preview = _depth_to_preview(depth)
        publisher.camera_frame(rgb, depth_preview, timestamp, preview_quality)

    def on_camera_status(status, device=None):
        publisher.camera_status(status, device)

    camera = create_camera_manager(
        app_config, frame_buffer, on_camera_frame, on_camera_status,
    )

    capture = CaptureManager(camera, datasets, metadata, storage,
                             publisher.emit)
    depth = DepthManager(frame_buffer, camera)

    ctx.storage = storage
    ctx.datasets = datasets
    ctx.statistics = stats
    ctx.camera = camera
    ctx.capture = capture
    ctx.depth = depth
    ctx.metadata = metadata

    from api import register_blueprints
    register_blueprints(app, ctx)

    socketio.init_app(app)

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({
            "success": False,
            "error": {"code": "NOT_FOUND", "message": "endpoint not found"},
        }), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)},
        }), 500

    @app.errorhandler(Exception)
    def unhandled(e):
        logger.exception("Unhandled error: %s", e)
        return jsonify({
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "internal server error"},
        }), 500

    return app


def _depth_to_preview(depth):
    import numpy as np

    d = depth.astype(np.float32)
    valid = d[d > 0]
    if valid.size == 0:
        return np.zeros(d.shape, dtype=np.uint8)
    normalized = np.clip((d - valid.min()) / max(valid.max() - valid.min(), 1) * 255,
                         0, 255).astype(np.uint8)
    return normalized


def start_background():
    camera = ctx.camera
    camera.start()


def shutdown():
    logger.info("Shutting down...")
    try:
        ctx.capture.stop()
    except Exception:
        pass
    try:
        ctx.camera.stop()
    except Exception:
        pass
    logger.info("Shutdown complete")


app = create_app()


@socketio.on("connect")
def on_ws_connect():
    logger.info("WebSocket client connected")


def main():
    signal.signal(signal.SIGTERM, lambda *_: shutdown())
    signal.signal(signal.SIGINT, lambda *_: (shutdown(), sys.exit(0)))

    logger.info("Starting RealSense Dataset Collector backend")
    logger.info("Mode: %s | Storage: %s",
                "mock" if app_config.mock_camera else "real",
                ctx.storage.root)
    start_background()

    try:
        socketio.run(app, host=app_config.host, port=app_config.port,
                     debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    finally:
        shutdown()


if __name__ == "__main__":
    main()
