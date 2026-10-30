from fastapi import APIRouter, Query

from app.api.deps import Captures
from app.schemas.capture import CaptureRequest, CaptureResult, NextName

router = APIRouter(prefix="/capture", tags=["capture"])


@router.post("", response_model=CaptureResult)
def capture(req: CaptureRequest, service: Captures) -> CaptureResult:
    # Sync endpoint: runs in the threadpool, so a long burst never blocks the event loop.
    return service.capture(req)


@router.get("/next-name", response_model=NextName)
def next_name(service: Captures, project_id: int = Query(), class_id: int = Query()) -> NextName:
    return service.next_name(project_id, class_id)
