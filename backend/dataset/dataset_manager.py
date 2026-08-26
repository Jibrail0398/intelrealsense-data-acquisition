import logging
import os
import threading

from dataset.label_manager import LabelManager


logger = logging.getLogger(__name__)

DATASET_PATTERN_MIN = 1


class DatasetManager:
    def __init__(self, storage_manager, metadata_manager):
        self._storage = storage_manager
        self._metadata = metadata_manager
        self.labels = LabelManager(storage_manager)
        self._id_lock = threading.Lock()

    @property
    def root(self):
        return self._storage.root

    @staticmethod
    def is_valid_name(name):
        return bool(name and LabelManager.is_valid_name(name))

    def dataset_path(self, dataset):
        return os.path.join(self.root, dataset)

    def rgb_dir(self, dataset, label):
        return os.path.join(self.root, dataset, label, "rgb")

    def depth_dir(self, dataset, label):
        return os.path.join(self.root, dataset, label, "depth")

    def create_dataset(self, name):
        if not self.is_valid_name(name):
            return False, "invalid dataset name"
        path = self.dataset_path(name)
        if os.path.exists(path):
            return False, "dataset already exists"
        os.makedirs(path, exist_ok=True)
        logger.info("Dataset created: %s", name)
        return True, None

    def list_datasets(self):
        if not os.path.isdir(self.root):
            return []
        return sorted(
            entry for entry in os.listdir(self.root)
            if os.path.isdir(os.path.join(self.root, entry))
        )

    def get_dataset(self, name):
        if not os.path.isdir(self.dataset_path(name)):
            return None
        labels = self.labels.list_labels(name)
        return {
            "name": name,
            "labels": [
                {"name": lb,
                 "count": self.count_captures(name, lb)}
                for lb in labels
            ],
        }

    def create_label(self, dataset, label):
        if not os.path.isdir(self.dataset_path(dataset)):
            return False, "dataset not found"
        ok, reason = self.labels.create_label(dataset, label)
        if not ok:
            return False, reason
        return True, None

    def count_captures(self, dataset, label):
        rgb_path = self.rgb_dir(dataset, label)
        if not os.path.isdir(rgb_path):
            return 0
        return len([f for f in os.listdir(rgb_path) if f.endswith(".png")])

    def next_id(self, dataset, label):
        with self._id_lock:
            rgb_path = self.rgb_dir(dataset, label)
            os.makedirs(rgb_path, exist_ok=True)
            max_id = 0
            for filename in os.listdir(rgb_path):
                base, ext = os.path.splitext(filename)
                if ext == ".png" and base.isdigit():
                    max_id = max(max_id, int(base))
            next_id = max_id + 1
            candidate = f"{next_id:06d}"
            while (os.path.exists(os.path.join(rgb_path, candidate + ".png")) or
                   os.path.exists(os.path.join(
                       self.depth_dir(dataset, label), candidate + ".npy"))):
                next_id += 1
                candidate = f"{next_id:06d}"
            return candidate

    def validate_dataset(self, name):
        issues = []
        if not os.path.isdir(self.dataset_path(name)):
            return {"valid": False, "issues": [{"id": None, "issue": "dataset_not_found"}]}
        for label in self.labels.list_labels(name):
            rgb_files = set()
            depth_files = set()
            rgb_path = self.rgb_dir(name, label)
            depth_path = self.depth_dir(name, label)
            if os.path.isdir(rgb_path):
                for f in os.listdir(rgb_path):
                    base, ext = os.path.splitext(f)
                    if ext == ".png":
                        rgb_files.add(base)
                        full = os.path.join(rgb_path, f)
                        if os.path.getsize(full) == 0:
                            issues.append({"id": base, "issue": "corrupted_png"})
            else:
                issues.append({"id": label, "issue": "missing_rgb_folder"})
            if os.path.isdir(depth_path):
                for f in os.listdir(depth_path):
                    base, ext = os.path.splitext(f)
                    if ext == ".npy":
                        depth_files.add(base)
                        full = os.path.join(depth_path, f)
                        if os.path.getsize(full) == 0:
                            issues.append({"id": base, "issue": "invalid_npy"})
            else:
                issues.append({"id": label, "issue": "missing_depth_folder"})
            seen = set()
            for capture_id in rgb_files | depth_files:
                if capture_id in seen:
                    issues.append({"id": capture_id, "issue": "duplicate_id"})
                seen.add(capture_id)
                if capture_id not in rgb_files:
                    issues.append({"id": capture_id, "issue": "missing_rgb"})
                if capture_id not in depth_files:
                    issues.append({"id": capture_id, "issue": "missing_depth"})
                elif capture_id not in depth_files and capture_id in rgb_files:
                    pass
        unpaired = [i["id"] for i in issues if i["issue"] in ("missing_rgb", "missing_depth")]
        valid = len(issues) == 0
        return {"valid": valid, "issues": issues}

    def delete_capture(self, capture_id, dataset=None, label=None):
        meta = None
        if dataset and label:
            meta = self._metadata.load(capture_id, dataset, label)
            target_ds, target_label = dataset, label
        else:
            found = self._metadata.find_capture(capture_id)
            if found:
                target_ds = found["dataset"]
                target_label = found["label"]
            elif dataset is None or label is None:
                found_by_scan = self._scan_for_capture(capture_id)
                if not found_by_scan:
                    return False, "capture not found"
                target_ds, target_label = found_by_scan
            else:
                return False, "capture not found"
        deleted_any = False
        png = os.path.join(self.rgb_dir(target_ds, target_label), capture_id + ".png")
        npy = os.path.join(self.depth_dir(target_ds, target_label), capture_id + ".npy")
        try:
            if os.path.exists(png):
                os.remove(png)
                deleted_any = True
            if os.path.exists(npy):
                os.remove(npy)
                deleted_any = True
            self._metadata.delete(capture_id, target_ds, target_label)
        except OSError as exc:
            logger.error("Delete failed: %s", exc)
            return False, str(exc)
        logger.info("Deleted capture %s from %s/%s", capture_id, target_ds, target_label)
        return deleted_any, None

    def _scan_for_capture(self, capture_id):
        for ds in self.list_datasets():
            for lb in self.labels.list_labels(ds):
                png = os.path.join(self.rgb_dir(ds, lb), capture_id + ".png")
                npy = os.path.join(self.depth_dir(ds, lb), capture_id + ".npy")
                if os.path.exists(png) or os.path.exists(npy):
                    return ds, lb
        return None

    def retake_capture(self, capture_id, dataset=None, label=None):
        meta = self._metadata.find_capture(capture_id) if not (dataset and label) \
            else self._metadata.load(capture_id, dataset, label)
        if meta:
            target_ds, target_label = meta["dataset"], meta["label"]
        else:
            scanned = self._scan_for_capture(capture_id)
            if not scanned:
                return None, "capture not found"
            target_ds, target_label = scanned
        ok, reason = self.delete_capture(capture_id, target_ds, target_label)
        if not ok:
            return None, reason
        new_id = self.next_id(target_ds, target_label)
        logger.info("Retake: %s -> %s (%s/%s)", capture_id, new_id, target_ds, target_label)
        return {
            "previous_id": capture_id,
            "new_id": new_id,
            "dataset": target_ds,
            "label": target_label,
        }, None
