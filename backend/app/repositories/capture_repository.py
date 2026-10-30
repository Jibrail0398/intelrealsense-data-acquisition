from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models import CaptureRecord


class CaptureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_many(self, records: list[CaptureRecord]) -> list[CaptureRecord]:
        self.db.add_all(records)
        self.db.flush()
        return records

    def get(self, capture_id: int) -> CaptureRecord | None:
        stmt = select(CaptureRecord).options(joinedload(CaptureRecord.project)).where(CaptureRecord.id == capture_id)
        return self.db.scalar(stmt)

    def delete(self, record: CaptureRecord) -> None:
        self.db.delete(record)

    def max_index(self, project_id: int, class_name: str) -> int:
        stmt = select(func.max(CaptureRecord.index)).where(
            CaptureRecord.project_id == project_id, CaptureRecord.class_name == class_name
        )
        return self.db.scalar(stmt) or 0

    def for_project(self, project_id: int) -> list[CaptureRecord]:
        return list(self.db.scalars(select(CaptureRecord).where(CaptureRecord.project_id == project_id)))

    def for_class(self, project_id: int, class_name: str) -> list[CaptureRecord]:
        stmt = select(CaptureRecord).where(
            CaptureRecord.project_id == project_id, CaptureRecord.class_name == class_name
        )
        return list(self.db.scalars(stmt))

    def rename_class(self, project_id: int, class_id: int, new_name: str) -> None:
        self.db.execute(
            update(CaptureRecord)
            .where(CaptureRecord.project_id == project_id, CaptureRecord.class_id == class_id)
            .values(class_name=new_name)
        )

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
    ) -> tuple[list[CaptureRecord], int]:
        conditions = []
        if project_id is not None:
            conditions.append(CaptureRecord.project_id == project_id)
        if class_name:
            conditions.append(CaptureRecord.class_name == class_name)
        if date_from is not None:
            conditions.append(CaptureRecord.captured_at >= date_from)
        if date_to is not None:
            conditions.append(CaptureRecord.captured_at < date_to)
        if query:
            conditions.append(CaptureRecord.image_name.ilike(f"%{query}%"))

        total = self.db.scalar(select(func.count()).select_from(CaptureRecord).where(*conditions)) or 0
        stmt = (
            select(CaptureRecord)
            .options(joinedload(CaptureRecord.project))
            .where(*conditions)
            .order_by(CaptureRecord.captured_at.desc(), CaptureRecord.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt)), total
