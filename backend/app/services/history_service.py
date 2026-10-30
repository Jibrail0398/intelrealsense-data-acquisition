from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import CaptureRecord
from app.repositories.capture_repository import CaptureRepository
from app.schemas.camera import PreviewConfig
from app.schemas.capture import CaptureOut, HistoryPage
from app.services.camera.preview import colorize_depth, encode_jpeg
from app.services.event_hub import EventHub
from app.utils.time import as_utc

THUMB_WIDTH = 240


class HistoryService:
    def __init__(self, db: Session, hub: EventHub) -> None:
        self.db = db
        self.hub = hub
        self.repo = CaptureRepository(db)

    def search(
        self,
        *,
        project_id: int | None,
        class_name: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        query: str | None,
        limit: int,
        offset: int,
    ) -> HistoryPage:
        rows, total = self.repo.search(
            project_id=project_id, class_name=class_name,
            date_from=as_utc(date_from) if date_from else None,
            date_to=as_utc(date_to) if date_to else None,
            query=query, limit=limit, offset=offset,
        )
        return HistoryPage(items=[self._out(r) for r in rows], total=total, limit=limit, offset=offset)

    def thumbnail(self, capture_id: int) -> bytes:
        record = self._require(capture_id)
        image = self._load_preview_source(record)
        if image is None:
            raise NotFoundError("The image files for this capture are no longer on disk")
        h, w = image.shape[:2]
        scale = THUMB_WIDTH / w
        thumb = cv2.resize(image, (THUMB_WIDTH, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)
        return encode_jpeg(thumb, 80)

    def delete(self, capture_id: int, delete_files: bool) -> None:
        record = self._require(capture_id)
        if delete_files:
            for raw in record.files.values():
                Path(raw).unlink(missing_ok=True)
        self.repo.delete(record)
        self.db.commit()
        self.hub.publish_threadsafe("capture.deleted", {"id": capture_id, "project_id": record.project_id})

    def _require(self, capture_id: int) -> CaptureRecord:
        record = self.repo.get(capture_id)
        if record is None:
            raise NotFoundError("Capture not found")
        return record

    @staticmethod
    def _load_preview_source(record: CaptureRecord) -> np.ndarray | None:
        for key in ("jpg", "png"):
            path = record.files.get(key)
            if path and Path(path).exists():
                data = np.fromfile(path, dtype=np.uint8)
                return cv2.imdecode(data, cv2.IMREAD_COLOR)
        for key in ("png16", "tiff", "npy"):
            path = record.files.get(key)
            if not path or not Path(path).exists():
                continue
            if key == "npy":
                depth = np.load(path, allow_pickle=False)
            else:
                depth = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            return colorize_depth(depth, record.depth_scale, PreviewConfig())
        return None

    @staticmethod
    def _out(record: CaptureRecord) -> CaptureOut:
        out = CaptureOut.model_validate(record)
        out.project_name = record.project.name if record.project else ""
        return out
