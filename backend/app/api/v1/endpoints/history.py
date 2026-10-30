from datetime import datetime

from fastapi import APIRouter, Query, Response, status

from app.api.deps import History
from app.schemas.capture import HistoryPage

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryPage)
def search_history(
    service: History,
    project_id: int | None = None,
    class_name: str | None = None,
    date_from: datetime | None = Query(None, description="Inclusive, ISO 8601"),
    date_to: datetime | None = Query(None, description="Exclusive, ISO 8601"),
    q: str | None = Query(None, description="Part of the image name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> HistoryPage:
    return service.search(
        project_id=project_id, class_name=class_name, date_from=date_from, date_to=date_to,
        query=q, limit=limit, offset=offset,
    )


@router.get("/{capture_id}/thumbnail")
def thumbnail(capture_id: int, service: History) -> Response:
    return Response(
        content=service.thumbnail(capture_id),
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.delete("/{capture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_capture(capture_id: int, service: History, delete_files: bool = True) -> None:
    service.delete(capture_id, delete_files)
