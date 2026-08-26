import json
import logging
import os
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataManager:
    def __init__(self, storage_manager):
        self._storage = storage_manager
        self._lock = threading.Lock()

    def _metadata_dir(self, dataset, label):
        return os.path.join(
            self._storage.root, dataset, label, "metadata"
        )

    def save(self, capture_id, dataset, label, rgb_rel, depth_rel,
             rgb_resolution, depth_resolution, fps, depth_scale):
        metadata_dir = self._metadata_dir(dataset, label)
        os.makedirs(metadata_dir, exist_ok=True)
        payload = {
            "capture_id": capture_id,
            "dataset": dataset,
            "label": label,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "rgb": rgb_rel,
            "depth": depth_rel,
            "rgb_resolution": list(rgb_resolution),
            "depth_resolution": list(depth_resolution),
            "fps": fps,
            "depth_scale": depth_scale,
        }
        path = os.path.join(metadata_dir, f"{capture_id}.json")
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_path, path)
        return path

    def load(self, capture_id, dataset, label):
        path = os.path.join(self._metadata_dir(dataset, label), f"{capture_id}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def delete(self, capture_id, dataset, label):
        path = os.path.join(self._metadata_dir(dataset, label), f"{capture_id}.json")
        if os.path.exists(path):
            os.remove(path)

    def find_capture(self, capture_id):
        root = self._storage.root
        for dataset in sorted(os.listdir(root)) if os.path.isdir(root) else []:
            ds_path = os.path.join(root, dataset)
            if not os.path.isdir(ds_path):
                continue
            for label in sorted(os.listdir(ds_path)):
                meta = self.load(capture_id, dataset, label)
                if meta:
                    return meta
        return None
