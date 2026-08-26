import logging


logger = logging.getLogger(__name__)

STATE_IDLE = "idle"
STATE_STARTING = "starting"
STATE_CAPTURING = "capturing"
STATE_COMPLETED = "completed"
STATE_STOPPED = "stopped"
STATE_ERROR = "error"


class CaptureWorker:
    def __init__(self, camera_manager, dataset_manager, metadata_manager,
                 storage_manager, emit_event):
        self.camera = camera_manager
        self.datasets = dataset_manager
        self.metadata = metadata_manager
        self.storage = storage_manager
        self.emit_event = emit_event
        self.last_result = None

    def save_frame_pair(self, dataset, label):
        from capture.capture_result import CaptureResult

        rgb, depth, timestamp = self.camera.frame_buffer.get_latest()
        if rgb is None or depth is None:
            return None, "no frame available"

        capture_id = self.datasets.next_id(dataset, label)
        rgb_dir = self.datasets.rgb_dir(dataset, label)
        depth_dir = self.datasets.depth_dir(dataset, label)

        import os
        os.makedirs(rgb_dir, exist_ok=True)
        os.makedirs(depth_dir, exist_ok=True)

        rgb_path_abs = os.path.join(rgb_dir, capture_id + ".png")
        depth_path_abs = os.path.join(depth_dir, capture_id + ".npy")
        result = CaptureResult(capture_id)

        try:
            import cv2
            import numpy as np
            from storage.file_manager import FileManager

            FileManager.safe_write(
                rgb_path_abs,
                lambda f: f.write(cv2.imencode(".png", rgb)[1].tobytes()),
            )
            result.rgb_saved = FileManager.exists(rgb_path_abs)
            result.rgb_path = f"{dataset}/{label}/rgb/{capture_id}.png"

            np.save(depth_path_abs + ".tmp.npy", depth)
            os.replace(depth_path_abs + ".tmp.npy", depth_path_abs)
            result.depth_saved = FileManager.exists(depth_path_abs)
            result.depth_path = f"{dataset}/{label}/depth/{capture_id}.npy"

            if not result.paired:
                FileManager.cleanup_partial([rgb_path_abs, depth_path_abs])
                return result, "save failed"

            cfg = self.camera.get_settings()
            self.metadata.save(
                capture_id, dataset, label, result.rgb_path, result.depth_path,
                (rgb.shape[1], rgb.shape[0]), (depth.shape[1], depth.shape[0]),
                cfg["fps"], self.camera.get_depth_scale(),
            )
            logger.info("Saved capture %s (%s/%s)", capture_id, dataset, label)
            self.last_result = result.to_dict()
            return result, None
        except Exception as exc:
            logger.error("Capture save error: %s", exc)
            return result, str(exc)
