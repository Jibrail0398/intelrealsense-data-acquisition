import logging
import os
import threading
import time

from capture.capture_worker import CaptureWorker
from capture.capture_worker import (
    STATE_CAPTURING,
    STATE_COMPLETED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_STARTING,
    STATE_STOPPED,
)

logger = logging.getLogger(__name__)

VALID_MODES = ("single", "burst", "continuous")
MIN_FREE_ESTIMATE_BYTES = 100 * 1024 * 1024


class CaptureManager:
    def __init__(self, camera_manager, dataset_manager, metadata_manager,
                 storage_manager, emit_event):
        self.camera = camera_manager
        self.datasets = dataset_manager
        self.metadata = metadata_manager
        self.storage = storage_manager
        self.emit_event = emit_event
        self.worker = CaptureWorker(
            camera_manager, dataset_manager, metadata_manager,
            storage_manager, emit_event,
        )
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self.state = STATE_IDLE
        self.progress = {"current": 0, "total": 0}
        self.session = {}

    def get_status(self):
        return {
            "state": self.state,
            "progress": dict(self.progress),
            "session": dict(self.session),
        }

    def _set_state(self, state):
        self.state = state

    def start(self, mode, dataset, label, count=1, interval_ms=200):
        if mode not in VALID_MODES:
            return False, {
                "code": "INVALID_CAPTURE_CONFIGURATION",
                "message": f"mode must be one of {VALID_MODES}",
            }
        if not self.datasets.is_valid_name(dataset) or \
                not self.datasets.labels.is_valid_name(label):
            return False, {
                "code": "INVALID_LABEL",
                "message": "invalid dataset or label name",
            }
        with self._lock:
            if self.state in (STATE_STARTING, STATE_CAPTURING):
                return False, {
                    "code": "CAPTURE_IN_PROGRESS",
                    "message": "Another capture operation is currently running.",
                }
            ok, reason, _ = self.storage.can_capture(MIN_FREE_ESTIMATE_BYTES)
            if not ok:
                return False, {
                    "code": "INSUFFICIENT_STORAGE",
                    "message": reason,
                }
            if not os.path.isdir(self.datasets.dataset_path(dataset)):
                return False, {
                    "code": "INVALID_DATASET",
                    "message": f"dataset '{dataset}' does not exist",
                }
            label_path = os.path.join(self.datasets.dataset_path(dataset), label)
            if not os.path.isdir(label_path):
                return False, {
                    "code": "INVALID_LABEL",
                    "message": f"label '{label}' does not exist",
                }
            if mode != "continuous":
                try:
                    count = int(count)
                    interval_ms = int(interval_ms)
                except (TypeError, ValueError):
                    return False, {
                        "code": "INVALID_CAPTURE_CONFIGURATION",
                        "message": "count and interval_ms must be integers",
                    }
                if count < 1 or count > 10000 or interval_ms < 0 or interval_ms > 60000:
                    return False, {
                        "code": "INVALID_CAPTURE_CONFIGURATION",
                        "message": "count must be 1-10000 and interval_ms 0-60000",
                    }
            else:
                count = 0
                interval_ms = max(int(interval_ms or 0), 0)

            self._set_state(STATE_STARTING)
            self.session = {"mode": mode, "dataset": dataset, "label": label}
            self.progress = {"current": 0, "total": count}

            self._thread = threading.Thread(
                target=self._run_session,
                args=(mode, dataset, label, count, interval_ms),
                daemon=True,
                name="capture-worker",
            )
            self._thread.start()
        return True, None

    def stop(self):
        with self._lock:
            if self.state != STATE_CAPTURING and self.state != STATE_STARTING:
                return False, {
                    "code": "CAPTURE_ERROR",
                    "message": "no active capture session",
                }
            self._stop_event.set()
        logger.info("Capture stop requested")
        return True, None

    def _wait_for_frames(self, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline and not self._stop_event.is_set():
            if self.camera.frame_buffer.has_frames():
                return True
            time.sleep(0.02)
        return False

    def _run_session(self, mode, dataset, label, count, interval_ms):
        failed = None
        results = []
        try:
            self.emit_event("capture.started", {
                "mode": mode, "dataset": dataset, "label": label,
                "total": count,
            })
            logger.info("Capture started: mode=%s count=%s dataset=%s label=%s",
                        mode, count, dataset, label)
            self._set_state(STATE_CAPTURING)
            self._stop_event.clear()

            if not self._wait_for_frames():
                raise RuntimeError("camera frames unavailable")

            index = 0
            while not self._stop_event.is_set():
                result, error = self.worker.save_frame_pair(dataset, label)
                if error and "no frame" not in (error or ""):
                    raise RuntimeError(error)
                if result is None:
                    raise RuntimeError("no frame available")

                index += 1
                results.append(result.to_dict())
                self.progress = {"current": index, "total": count if count else 0}
                self.emit_event("capture.progress", {
                    "capture_id": result.capture_id,
                    "current": index,
                    "total": count if count else 0,
                    "status": "capturing",
                    "paired": result.paired,
                })

                if mode == "single":
                    break
                if mode == "burst" and index >= count:
                    break
                if interval_ms > 0:
                    end_wait = time.time() + interval_ms / 1000.0
                    while time.time() < end_wait and not self._stop_event.is_set():
                        time.sleep(0.005)

            if self._stop_event.is_set() and mode == "continuous":
                self._set_state(STATE_STOPPED)
                status = "stopped"
            elif mode == "burst" and not self._stop_event.is_set() and index < count:
                pass
            else:
                self._set_state(STATE_COMPLETED)
                status = "completed"

            last_result = results[-1] if results else {}
            self.emit_event("capture.completed", {
                "capture_id": last_result.get("id"),
                "mode": mode,
                "dataset": dataset,
                "label": label,
                "captured": len(results),
                "rgb_saved": bool(last_result.get("rgb", {}).get("saved")),
                "depth_saved": bool(last_result.get("depth", {}).get("saved")),
                "paired": bool(last_result.get("paired")),
                "status": status,
                "results": results if mode == "single" else [],
            })
            logger.info("Capture %s: %d frame(s)", status, len(results))
        except Exception as exc:
            failed = str(exc)
            logger.error("Capture failed: %s", exc)
            self._set_state(STATE_ERROR)
            self.emit_event("capture.failed", {
                "mode": mode,
                "dataset": dataset,
                "label": label,
                "error": failed,
            })
        finally:
            self._stop_event.clear()
            self.emit_event("storage.updated", self.storage.get_info())
            self.emit_event("dataset.updated", {
                "dataset": dataset,
                "statistics": self._stats(dataset),
            })

    def _stats(self, dataset):
        from dataset.statistics import Statistics
        stats = Statistics(self.storage, self.metadata)
        return stats.compute(dataset)
