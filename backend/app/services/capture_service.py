"""Taking shots: one take produces N images (a burst), each an RGB/depth pair
from one synchronised frameset, written in every format the project selects."""

import threading
import time
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, CaptureBusyError, NotFoundError
from app.models import CaptureRecord, Project, ProjectClass
from app.repositories.capture_repository import CaptureRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.capture import CaptureOut, CaptureRequest, CaptureResult, NextName
from app.services.camera import CameraManager
from app.services.event_hub import EventHub
from app.services.image_writer import FORMATS, class_dir, output_path, write_shot
from app.services.settings_service import SettingsService
from app.utils.naming import image_name, max_index_in_dir

# One capture at a time across the whole app.
_capture_lock = threading.Lock()


class CaptureService:
    def __init__(self, db: Session, camera: CameraManager, hub: EventHub) -> None:
        self.db = db
        self.camera = camera
        self.hub = hub
        self.projects = ProjectRepository(db)
        self.captures = CaptureRepository(db)

    @staticmethod
    def is_busy() -> bool:
        return _capture_lock.locked()

    def next_name(self, project_id: int, class_id: int) -> NextName:
        project, cls = self._resolve(project_id, class_id)
        index = self._next_index(project, cls.name)
        name = image_name(cls.name, index)
        return NextName(
            image_name=name,
            index=index,
            paths={k: str(output_path(project.destination_dir, FORMATS[k], cls.name, name)) for k in project.formats},
        )

    def capture(self, req: CaptureRequest) -> CaptureResult:
        if not _capture_lock.acquire(blocking=False):
            raise CaptureBusyError("A capture is already running")
        try:
            return self._capture(req)
        finally:
            _capture_lock.release()

    def _capture(self, req: CaptureRequest) -> CaptureResult:
        project, cls = self._resolve(req.project_id, req.class_id)
        if not project.formats:
            raise AppError("This project has no output format selected")
        self.camera.require_connected()

        rules = SettingsService(self.db).capture_rules()
        count = req.images_per_take or rules.images_per_take
        interval = (req.burst_interval_ms if req.burst_interval_ms is not None else rules.burst_interval_ms) / 1000

        burst_id = uuid.uuid4().hex[:12]
        start_index = self._next_index(project, cls.name)
        latest = self.camera.latest()
        last_seq = latest.seq if latest else 0
        self.hub.publish_threadsafe("capture.started", {
            "burst_id": burst_id, "total": count, "project_id": project.id, "class_id": cls.id,
        })

        saved: list[CaptureOut] = []
        try:
            for i in range(count):
                if i and interval:
                    time.sleep(interval)
                frame = self.camera.wait_for_frame(last_seq)
                last_seq = frame.seq
                index = start_index + i
                name = image_name(cls.name, index)
                try:
                    files = write_shot(project.destination_dir, project.formats, cls.name, name,
                                       frame.color, frame.depth)
                except OSError as exc:
                    raise AppError(f"Could not write {name}: {exc.strerror or exc}") from exc

                h, w = frame.color.shape[:2]
                record = CaptureRecord(
                    project_id=project.id, class_id=cls.id, class_name=cls.name, image_name=name,
                    index=index, files=files, burst_id=burst_id, width=w, height=h,
                    depth_scale=frame.depth_scale,
                    meta={
                        "depth_shape": list(frame.depth.shape),
                        "intrinsics": frame.intrinsics,
                        "device": self._device_info(),
                        "frame_timestamp": frame.timestamp,
                    },
                )
                self.captures.add_many([record])
                self.db.commit()
                out = self._out(record, project)
                saved.append(out)
                self.hub.publish_threadsafe("capture.progress", {
                    "burst_id": burst_id, "done": i + 1, "total": count, "capture": out,
                })
        except Exception as exc:
            message = getattr(exc, "message", str(exc))
            self.hub.publish_threadsafe("capture.failed", {
                "burst_id": burst_id, "done": len(saved), "total": count, "message": message,
            })
            raise

        result = CaptureResult(burst_id=burst_id, captures=saved)
        self.hub.publish_threadsafe("capture.completed", result)
        return result

    # -- helpers -----------------------------------------------------------

    def _resolve(self, project_id: int, class_id: int) -> tuple[Project, ProjectClass]:
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        cls = next((c for c in project.classes if c.id == class_id), None)
        if cls is None:
            raise NotFoundError("Class not found in this project")
        return project, cls

    def _next_index(self, project: Project, class_name: str) -> int:
        """Continue after the highest index in the database *or* on disk, so nothing is overwritten."""
        on_disk = max(
            (max_index_in_dir(class_dir(project.destination_dir, f, class_name), class_name) for f in FORMATS.values()),
            default=0,
        )
        return max(on_disk, self.captures.max_index(project.id, class_name)) + 1

    def _device_info(self) -> dict:
        device = self.camera.device
        try:
            return device.info() if device else {}
        except RuntimeError:
            return {}

    @staticmethod
    def _out(record: CaptureRecord, project: Project) -> CaptureOut:
        out = CaptureOut.model_validate(record)
        out.project_name = project.name
        return out
