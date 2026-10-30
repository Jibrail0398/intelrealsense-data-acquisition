from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.camera import CameraManager
from app.services.camera_service import CameraService
from app.services.capture_service import CaptureService
from app.services.event_hub import EventHub
from app.services.history_service import HistoryService
from app.services.project_service import ProjectService
from app.services.settings_service import SettingsService

DbSession = Annotated[Session, Depends(get_session)]


def get_camera(request: Request) -> CameraManager:
    return request.app.state.camera


def get_hub(request: Request) -> EventHub:
    return request.app.state.hub


Camera = Annotated[CameraManager, Depends(get_camera)]
Hub = Annotated[EventHub, Depends(get_hub)]


def get_project_service(db: DbSession, hub: Hub) -> ProjectService:
    return ProjectService(db, hub)


def get_capture_service(db: DbSession, camera: Camera, hub: Hub) -> CaptureService:
    return CaptureService(db, camera, hub)


def get_history_service(db: DbSession, hub: Hub) -> HistoryService:
    return HistoryService(db, hub)


def get_camera_service(db: DbSession, camera: Camera, hub: Hub) -> CameraService:
    return CameraService(db, camera, hub)


def get_settings_service(db: DbSession) -> SettingsService:
    return SettingsService(db)


Projects = Annotated[ProjectService, Depends(get_project_service)]
Captures = Annotated[CaptureService, Depends(get_capture_service)]
History = Annotated[HistoryService, Depends(get_history_service)]
CameraSvc = Annotated[CameraService, Depends(get_camera_service)]
SettingsSvc = Annotated[SettingsService, Depends(get_settings_service)]
