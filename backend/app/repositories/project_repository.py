from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import CaptureRecord, Project, ProjectClass


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Project]:
        stmt = select(Project).options(selectinload(Project.classes)).order_by(Project.updated_at.desc())
        return list(self.db.scalars(stmt))

    def get(self, project_id: int) -> Project | None:
        stmt = select(Project).options(selectinload(Project.classes)).where(Project.id == project_id)
        return self.db.scalar(stmt)

    def get_by_name(self, name: str) -> Project | None:
        return self.db.scalar(select(Project).where(func.lower(Project.name) == name.lower()))

    def add(self, project: Project) -> Project:
        self.db.add(project)
        self.db.flush()
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)

    def get_class(self, project_id: int, class_id: int) -> ProjectClass | None:
        return self.db.scalar(
            select(ProjectClass).where(ProjectClass.project_id == project_id, ProjectClass.id == class_id)
        )

    def class_counts(self, project_id: int) -> dict[int, int]:
        stmt = (
            select(CaptureRecord.class_id, func.count())
            .where(CaptureRecord.project_id == project_id, CaptureRecord.class_id.is_not(None))
            .group_by(CaptureRecord.class_id)
        )
        return {cid: n for cid, n in self.db.execute(stmt)}

    def total_counts(self) -> dict[int, int]:
        stmt = select(CaptureRecord.project_id, func.count()).group_by(CaptureRecord.project_id)
        return {pid: n for pid, n in self.db.execute(stmt)}
