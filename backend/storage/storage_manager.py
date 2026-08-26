import logging
import os
import shutil
import threading


logger = logging.getLogger(__name__)

BYTES_PER_GB = 1024 ** 3


class StorageManager:
    def __init__(self, config):
        self._config = config
        self._lock = threading.Lock()
        self.root = config.storage_path

    def set_root(self, path):
        path = os.path.abspath(os.path.expanduser(path))
        if not self.is_writable(path):
            return False, "path not writable"
        with self._lock:
            self.root = path
            self._config.storage_path = path
        logger.info("Storage root changed: %s", path)
        return True, None

    def get_info(self):
        total, free = self.disk_usage()
        dataset_bytes = self.dataset_size()
        return {
            "path": self.root,
            "total_bytes": total,
            "free_bytes": free,
            "dataset_bytes": dataset_bytes,
            "minimum_free_space_gb": self._config.minimum_free_space_gb,
            "low_storage": free < self.minimum_free_bytes(),
        }

    def disk_usage(self):
        try:
            usage = shutil.disk_usage(self.root)
            return usage.total, usage.free
        except OSError:
            return 0, 0

    def minimum_free_bytes(self):
        return int(self._config.minimum_free_space_gb * BYTES_PER_GB)

    def dataset_size(self):
        total = 0
        for dirpath, _, filenames in os.walk(self.root):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
        return total

    @staticmethod
    def is_writable(path):
        try:
            if os.path.exists(path):
                return os.access(path, os.W_OK)
            test_dir = os.path.dirname(path) or "."
            probe = os.path.join(test_dir, ".write_probe_tmp")
            with open(probe, "w") as f:
                f.write("probe")
            os.remove(probe)
            return True
        except OSError:
            return False

    def ensure_root(self):
        try:
            os.makedirs(self.root, exist_ok=True)
            return True
        except OSError as exc:
            logger.error("Cannot create storage root: %s", exc)
            return False

    def can_capture(self, estimated_bytes=50 * 1024 * 1024):
        checks = {
            "path_exists": os.path.isdir(self.root),
            "writable": self.is_writable(self.root),
        }
        _, free = self.disk_usage()
        checks["enough_space"] = free > max(
            self.minimum_free_bytes(), estimated_bytes
        )
        if all(checks.values()):
            return True, None, checks
        if not checks["enough_space"]:
            reason = "insufficient_storage"
        elif not checks["writable"]:
            reason = "storage_not_writable"
        else:
            reason = "storage_path_missing"
        return False, reason, checks
