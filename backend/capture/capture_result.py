class CaptureResult:
    def __init__(self, capture_id, rgb_saved=False, depth_saved=False,
                 rgb_path=None, depth_path=None):
        self.capture_id = capture_id
        self.rgb_saved = rgb_saved
        self.depth_saved = depth_saved
        self.rgb_path = rgb_path
        self.depth_path = depth_path

    @property
    def paired(self):
        return self.rgb_saved and self.depth_saved

    def to_dict(self):
        return {
            "id": self.capture_id,
            "rgb": {"saved": self.rgb_saved, "path": self.rgb_path},
            "depth": {"saved": self.depth_saved, "path": self.depth_path},
            "paired": self.paired,
        }
