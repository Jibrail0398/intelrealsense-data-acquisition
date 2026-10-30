from fastapi import APIRouter

from app.api.deps import Hub, Projects, SettingsSvc
from app.core.exceptions import NotFoundError
from app.schemas.settings import CaptureRules, SessionState

router = APIRouter(tags=["settings"])


@router.get("/settings/capture-rules", response_model=CaptureRules)
def get_capture_rules(settings: SettingsSvc) -> CaptureRules:
    return settings.capture_rules()


@router.put("/settings/capture-rules", response_model=CaptureRules)
def save_capture_rules(rules: CaptureRules, settings: SettingsSvc, hub: Hub) -> CaptureRules:
    saved = settings.save_capture_rules(rules)
    hub.publish_threadsafe("settings.capture_rules", saved)
    return saved


@router.get("/session", response_model=SessionState)
def get_session(settings: SettingsSvc) -> SessionState:
    return settings.session()


@router.put("/session", response_model=SessionState)
def save_session(state: SessionState, settings: SettingsSvc, projects: Projects) -> SessionState:
    """The project and class the capture screen points at; decides where shots are saved."""
    if state.active_project_id is not None:
        project = projects.require(state.active_project_id)
        if state.active_class_id is not None and all(c.id != state.active_class_id for c in project.classes):
            raise NotFoundError("Class not found in this project")
        if state.active_class_id is None and project.classes:
            state.active_class_id = min(project.classes, key=lambda c: c.position).id
    else:
        state.active_class_id = None
    return settings.save_session(state)
