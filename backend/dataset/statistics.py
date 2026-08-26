import logging
import os

from dataset.dataset_manager import DatasetManager
from dataset.metadata_manager import MetadataManager
from dataset.label_manager import LabelManager


logger = logging.getLogger(__name__)


class Statistics:
    def __init__(self, storage_manager, metadata_manager=None):
        self._storage = storage_manager
        self.datasets = DatasetManager(storage_manager, metadata_manager)
        self.labels = LabelManager(storage_manager)

    def compute(self, dataset_name):
        result = {
            "total": 0,
            "labels": {},
            "rgb_count": 0,
            "depth_count": 0,
            "paired": 0,
            "dataset_bytes": 0,
        }
        dataset_path = os.path.join(self._storage.root, dataset_name)
        if not os.path.isdir(dataset_path):
            return None
        for label in self.labels.list_labels(dataset_name):
            rgb_path = os.path.join(dataset_path, label, "rgb")
            depth_path = os.path.join(dataset_path, label, "depth")
            rgb_ids = set()
            depth_ids = set()
            size = 0
            if os.path.isdir(rgb_path):
                for f in os.listdir(rgb_path):
                    fp = os.path.join(rgb_path, f)
                    size += os.path.getsize(fp)
                    if f.endswith(".png"):
                        rgb_ids.add(os.path.splitext(f)[0])
            if os.path.isdir(depth_path):
                for f in os.listdir(depth_path):
                    fp = os.path.join(depth_path, f)
                    size += os.path.getsize(fp)
                    if f.endswith(".npy"):
                        depth_ids.add(os.path.splitext(f)[0])
            paired_ids = rgb_ids & depth_ids
            count = len(rgb_ids | depth_ids)
            result["labels"][label] = count
            result["total"] += count
            result["rgb_count"] += len(rgb_ids)
            result["depth_count"] += len(depth_ids)
            result["paired"] += len(paired_ids)
            result["dataset_bytes"] += size
        return result
