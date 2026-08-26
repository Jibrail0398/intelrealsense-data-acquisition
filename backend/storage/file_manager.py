import logging
import os


logger = logging.getLogger(__name__)


class FileManager:
    @staticmethod
    def safe_write(path, writer):
        tmp_path = path + ".tmp"
        with open(tmp_path, "wb") as f:
            writer(f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    @staticmethod
    def remove(*paths):
        removed = False
        for path in paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    removed = True
            except OSError as exc:
                logger.error("Failed to remove %s: %s", path, exc)
        return removed

    @staticmethod
    def cleanup_partial(paths):
        FileManager.remove(*paths)
