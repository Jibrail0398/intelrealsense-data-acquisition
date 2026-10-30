"""Persisted app state: the active project/class, capture rules, camera config."""

from sqlalchemy.orm import Session

from app.repositories.setting_repository import SettingRepository
from app.schemas.camera import CameraConfig
from app.schemas.settings import CaptureRules, SessionState

SESSION_KEY = "session"
CAPTURE_RULES_KEY = "capture_rules"
CAMERA_KEY = "camera"


class SettingsService:
    def __init__(self, db: Session) -> None:
        self.repo = SettingRepository(db)

    def session(self) -> SessionState:
        return self.repo.load(SESSION_KEY, SessionState)

    def save_session(self, value: SessionState) -> SessionState:
        self.repo.save(SESSION_KEY, value)
        return value

    def capture_rules(self) -> CaptureRules:
        return self.repo.load(CAPTURE_RULES_KEY, CaptureRules)

    def save_capture_rules(self, value: CaptureRules) -> CaptureRules:
        self.repo.save(CAPTURE_RULES_KEY, value)
        return value

    def camera_config(self) -> CameraConfig:
        return self.repo.load(CAMERA_KEY, CameraConfig)

    def save_camera_config(self, value: CameraConfig) -> CameraConfig:
        self.repo.save(CAMERA_KEY, value)
        return value
