import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "app_config.json")

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 5000,
    "storage_path": os.path.join(BASE_DIR, "datasets"),
    "minimum_free_space_gb": 5,
    "mock_camera": True,
    "camera": {
        "rgb_resolution": [640, 480],
        "depth_resolution": [640, 480],
        "fps": 30,
        "exposure": "auto",
        "white_balance": "auto",
    },
    "preview": {
        "jpeg_quality": 70,
        "target_fps": 15,
    },
}


class Config:
    def __init__(self, path=CONFIG_PATH):
        self._path = path
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    loaded = json.load(f)
                for key, value in loaded.items():
                    if isinstance(value, dict) and isinstance(self._data.get(key), dict):
                        self._data[key].update(value)
                    else:
                        self._data[key] = value
            except (json.JSONDecodeError, OSError):
                pass
        if os.environ.get("MOCK_CAMERA") is not None:
            self._data["mock_camera"] = os.environ["MOCK_CAMERA"].lower() in ("1", "true", "yes")
        if os.environ.get("STORAGE_PATH"):
            self._data["storage_path"] = os.environ["STORAGE_PATH"]

    @property
    def host(self):
        return self._data["host"]

    @property
    def port(self):
        return self._data["port"]

    @property
    def storage_path(self):
        return self._data["storage_path"]

    @storage_path.setter
    def storage_path(self, value):
        self._data["storage_path"] = value
        self.save()

    @property
    def minimum_free_space_gb(self):
        return self._data["minimum_free_space_gb"]

    @property
    def mock_camera(self):
        return self._data["mock_camera"]

    @property
    def camera(self):
        return self._data["camera"]

    @property
    def preview(self):
        return self._data["preview"]

    def update_camera_settings(self, settings):
        self._data["camera"].update(settings)
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)


config = Config()
