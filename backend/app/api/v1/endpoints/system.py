from fastapi import APIRouter, Query
from fastapi.concurrency import run_in_threadpool

from app.api.deps import Camera
from app.core.config import get_settings
from app.schemas.system import CreateDirectory, DirectoryEntry, DirectoryListing, PickedDirectory
from app.services import directory_service
from app.services.capture_service import CaptureService

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health(camera: Camera) -> dict:
    return {
        "status": "ok",
        "app": get_settings().app_name,
        "camera_backend": camera.backend,
        "capture_busy": CaptureService.is_busy(),
    }


@router.post("/pick-directory", response_model=PickedDirectory)
async def pick_directory(initial: str | None = None) -> PickedDirectory:
    """Open the OS folder dialog on this machine and return the chosen path."""
    return await run_in_threadpool(directory_service.pick_directory, initial)


@router.get("/directories", response_model=DirectoryListing)
def list_directories(path: str | None = Query(None)) -> DirectoryListing:
    return directory_service.list_directory(path)


@router.post("/directories", response_model=DirectoryEntry, status_code=201)
def create_directory(req: CreateDirectory) -> DirectoryEntry:
    return directory_service.create_directory(req.parent, req.name)
