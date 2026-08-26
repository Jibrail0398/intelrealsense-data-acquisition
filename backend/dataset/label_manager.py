import logging
import os
import re


logger = logging.getLogger(__name__)

LABEL_PATTERN = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


class LabelManager:
    def __init__(self, storage_manager):
        self._storage = storage_manager

    @staticmethod
    def is_valid_name(name):
        return bool(name and LABEL_PATTERN.match(name))

    def labels_dir(self, dataset):
        return os.path.join(self._storage.root, dataset)

    def create_label(self, dataset, label):
        if not self.is_valid_name(label) or not self.is_valid_name(dataset):
            return False, "invalid name"
        label_path = os.path.join(self.labels_dir(dataset), label, "rgb")
        if os.path.exists(label_path):
            return False, "label already exists"
        depth_path = os.path.join(self.labels_dir(dataset), label, "depth")
        os.makedirs(label_path, exist_ok=True)
        os.makedirs(depth_path, exist_ok=True)
        logger.info("Label created: %s/%s", dataset, label)
        return True, None

    def list_labels(self, dataset):
        dataset_path = os.path.join(self._storage.root, dataset)
        if not os.path.isdir(dataset_path):
            return []
        labels = []
        for entry in sorted(os.listdir(dataset_path)):
            if os.path.isdir(os.path.join(dataset_path, entry)):
                labels.append(entry)
        return labels
