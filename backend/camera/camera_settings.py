DEFAULT_RGB_RESOLUTIONS = [
    [320, 240],
    [424, 240],
    [640, 360],
    [640, 480],
    [848, 480],
    [960, 540],
    [1280, 720],
    [1920, 1080],
]

DEFAULT_DEPTH_RESOLUTIONS = [
    [320, 240],
    [424, 240],
    [640, 360],
    [640, 480],
    [848, 480],
    [1280, 720],
]

DEFAULT_FPS = [6, 15, 30, 60]

DEFAULT_SETTINGS = {
    "rgb_resolution": [640, 480],
    "depth_resolution": [640, 480],
    "fps": 30,
    "exposure": "auto",
    "white_balance": "auto",
}


class CameraSettings:
    def __init__(self):
        self.settings = dict(DEFAULT_SETTINGS)

    def get(self):
        return dict(self.settings)

    def validate(self, settings, capabilities):
        errors = []
        rgb_res = settings.get("rgb_resolution", self.settings["rgb_resolution"])
        depth_res = settings.get("depth_resolution", self.settings["depth_resolution"])
        fps = settings.get("fps", self.settings["fps"])

        if list(rgb_res) not in capabilities["rgb_resolutions"]:
            errors.append("rgb_resolution not supported")
        if list(depth_res) not in capabilities["depth_resolutions"]:
            errors.append("depth_resolution not supported")
        if fps not in capabilities["fps"]:
            errors.append("fps not supported")

        exposure = settings.get("exposure", self.settings["exposure"])
        if exposure != "auto" and (not isinstance(exposure, (int, float)) or exposure <= 0):
            errors.append("exposure must be 'auto' or a positive number")

        wb = settings.get("white_balance", self.settings["white_balance"])
        if wb != "auto" and (not isinstance(wb, (int, float)) or wb <= 0):
            errors.append("white_balance must be 'auto' or a positive number")

        if errors:
            return False, errors
        return True, []

    def update(self, settings):
        self.settings.update(settings)
