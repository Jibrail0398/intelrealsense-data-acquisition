"""Projects, their classes, and the folder tree they own on disk."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.models import Project, ProjectClass
from app.repositories.capture_repository import CaptureRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ClassOut, ProjectCreate, ProjectDeleteResult, ProjectOut, ProjectUpdate
from app.services.event_hub import EventHub
from app.services.image_writer import FORMATS, class_dir
from app.services.project_cleanup import CleanupResult, delete_project_files, owned_dirs
from app.services.settings_service import SettingsService
from app.utils.naming import image_name, parse_index


class ProjectService:
    def __init__(self, db: Session, hub: EventHub) -> None:
        self.db = db
        self.hub = hub
        self.projects = ProjectRepository(db)
        self.captures = CaptureRepository(db)

    # -- reading -----------------------------------------------------------

    def list_all(self) -> list[ProjectOut]:
        totals = self.projects.total_counts()
        return [self._out(p, totals.get(p.id, 0)) for p in self.projects.list_all()]

    def get(self, project_id: int) -> ProjectOut:
        project = self._require(project_id)
        return self._out(project, self.projects.total_counts().get(project.id, 0))

    def require(self, project_id: int) -> Project:
        return self._require(project_id)

    # -- projects ----------------------------------------------------------

    def create(self, data: ProjectCreate) -> ProjectOut:
        if self.projects.get_by_name(data.name):
            raise ConflictError(f'A project named "{data.name}" already exists')
        destination = self._prepare_destination(data.destination_dir)
        project = Project(name=data.name, destination_dir=str(destination), formats=data.formats)
        project.classes = [ProjectClass(name=n, position=i) for i, n in enumerate(data.classes)]
        self.projects.add(project)
        self.db.commit()
        self._ensure_tree(project)
        self._changed(project.id)
        return self.get(project.id)

    def update(self, project_id: int, data: ProjectUpdate) -> ProjectOut:
        project = self._require(project_id)
        if data.name is not None:
            name = data.name.strip()
            other = self.projects.get_by_name(name)
            if other and other.id != project.id:
                raise ConflictError(f'A project named "{name}" already exists')
            project.name = name
        if data.destination_dir is not None:
            project.destination_dir = str(self._prepare_destination(data.destination_dir))
        if data.formats is not None:
            project.formats = data.formats
        self.db.commit()
        self._ensure_tree(project)
        self._changed(project.id)
        return self.get(project.id)

    def delete(self, project_id: int, delete_files: bool = False) -> ProjectDeleteResult:
        project = self._require(project_id)
        records = self.captures.for_project(project.id)
        protected: set[Path] = set()
        if delete_files:
            for other in self.projects.list_all():
                if other.id != project.id:
                    protected |= owned_dirs(other, self.captures.for_project(other.id))

        self.projects.delete(project)
        self.db.commit()
        settings = SettingsService(self.db)
        session = settings.session()
        if session.active_project_id == project_id:
            settings.save_session(session.model_copy(update={"active_project_id": None, "active_class_id": None}))

        cleanup = delete_project_files(project, records, protected) if delete_files else CleanupResult()
        self.hub.publish_threadsafe("project.deleted", {"id": project_id})
        return ProjectDeleteResult(
            deleted_captures=len(records),
            deleted_files=cleanup.deleted_files,
            deleted_folders=cleanup.deleted_folders,
            errors=cleanup.errors,
        )

    # -- classes -----------------------------------------------------------

    def add_class(self, project_id: int, name: str) -> ProjectOut:
        project = self._require(project_id)
        self._assert_unique_class(project, name)
        position = max((c.position for c in project.classes), default=-1) + 1
        project.classes.append(ProjectClass(name=name, position=position))
        self.db.commit()
        self._ensure_tree(project)
        self._changed(project.id)
        return self.get(project.id)

    def rename_class(self, project_id: int, class_id: int, new_name: str) -> ProjectOut:
        project = self._require(project_id)
        cls = self._require_class(project_id, class_id)
        if cls.name == new_name:
            return self.get(project.id)
        self._assert_unique_class(project, new_name, ignore_id=cls.id)
        self._move_class_files(project, cls.name, new_name)
        self.captures.rename_class(project.id, cls.id, new_name)
        cls.name = new_name
        self.db.commit()
        self._ensure_tree(project)
        self._changed(project.id)
        return self.get(project.id)

    def delete_class(self, project_id: int, class_id: int) -> ProjectOut:
        project = self._require(project_id)
        cls = self._require_class(project_id, class_id)
        if len(project.classes) <= 1:
            raise AppError("A project needs at least one class")
        project.classes.remove(cls)
        self.db.commit()
        settings = SettingsService(self.db)
        session = settings.session()
        if session.active_class_id == class_id:
            settings.save_session(session.model_copy(update={"active_class_id": None}))
        self._changed(project.id)
        return self.get(project.id)

    def reorder_classes(self, project_id: int, class_ids: list[int]) -> ProjectOut:
        project = self._require(project_id)
        if sorted(class_ids) != sorted(c.id for c in project.classes):
            raise AppError("The new order must list every class of the project exactly once")
        position = {cid: i for i, cid in enumerate(class_ids)}
        for cls in project.classes:
            cls.position = position[cls.id]
        self.db.commit()
        self.db.refresh(project)
        self._changed(project.id)
        return self.get(project.id)

    # -- helpers -----------------------------------------------------------

    def _require(self, project_id: int) -> Project:
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        return project

    def _require_class(self, project_id: int, class_id: int) -> ProjectClass:
        cls = self.projects.get_class(project_id, class_id)
        if cls is None:
            raise NotFoundError("Class not found in this project")
        return cls

    @staticmethod
    def _assert_unique_class(project: Project, name: str, ignore_id: int | None = None) -> None:
        if any(c.name.lower() == name.lower() and c.id != ignore_id for c in project.classes):
            raise ConflictError(f'Class "{name}" already exists in this project')

    @staticmethod
    def _prepare_destination(raw: str) -> Path:
        path = Path(raw).expanduser()
        if not path.is_absolute():
            raise AppError("Destination folder must be an absolute path")
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise AppError(f"Cannot create destination folder: {exc.strerror}") from exc
        if not path.is_dir():
            raise AppError("Destination is not a folder")
        return path.resolve()

    @staticmethod
    def _ensure_tree(project: Project) -> None:
        """Create {dest}/{format}/{class}/ so the layout is visible before the first shot."""
        for key in project.formats:
            for cls in project.classes:
                try:
                    class_dir(project.destination_dir, FORMATS[key], cls.name).mkdir(parents=True, exist_ok=True)
                except OSError:
                    pass  # writing the first shot reports the real error

    def _move_class_files(self, project: Project, old: str, new: str) -> None:
        """Rename files `old-0001.ext` -> `new-0001.ext` and their class folders, all formats."""
        moves: list[tuple[Path, Path]] = []
        record_updates: list[tuple] = []
        for record in self.captures.for_class(project.id, old):
            new_files = {}
            for key, raw in record.files.items():
                src = Path(raw)
                dst = src.parent.parent / new / f"{image_name(new, record.index)}{src.suffix}"
                if src.exists():
                    moves.append((src, dst))
                new_files[key] = str(dst)
            record_updates.append((record, image_name(new, record.index), new_files))

        # Files on disk that the database does not track (e.g. from before a reinstall).
        tracked = {src for src, _ in moves}
        old_dirs = {class_dir(project.destination_dir, f, old) for f in FORMATS.values()}
        old_dirs |= {src.parent for src, _ in moves}
        for directory in old_dirs:
            if not directory.is_dir():
                continue
            for entry in directory.iterdir():
                idx = parse_index(entry.stem, old) if entry.is_file() else None
                if idx is not None and entry not in tracked:
                    moves.append((entry, directory.parent / new / f"{image_name(new, idx)}{entry.suffix}"))

        clashes = [dst for _, dst in moves if dst.exists()]
        if clashes:
            raise ConflictError(f"Cannot rename: {clashes[0]} already exists")

        done: list[tuple[Path, Path]] = []
        try:
            for src, dst in moves:
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dst)
                done.append((src, dst))
        except OSError as exc:
            for src, dst in reversed(done):
                dst.rename(src)
            raise AppError(f"Could not rename files on disk: {exc}") from exc

        for record, name, files in record_updates:
            record.image_name = name
            record.files = files
        for directory in old_dirs:
            try:
                directory.rmdir()  # only succeeds when empty
            except OSError:
                pass

    def _out(self, project: Project, total: int) -> ProjectOut:
        counts = self.projects.class_counts(project.id)
        return ProjectOut(
            id=project.id,
            name=project.name,
            destination_dir=project.destination_dir,
            formats=project.formats,
            classes=[
                ClassOut(id=c.id, name=c.name, position=c.position, count=counts.get(c.id, 0))
                for c in sorted(project.classes, key=lambda c: c.position)
            ],
            total_captures=total,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def _changed(self, project_id: int) -> None:
        self.hub.publish_threadsafe("project.updated", {"id": project_id})
