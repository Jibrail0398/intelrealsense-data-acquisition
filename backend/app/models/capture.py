from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.project import Project
from app.utils.time import utcnow


class CaptureRecord(Base):
    """One shot: an RGB/depth pair from one frameset, written in every selected format."""

    __tablename__ = "captures"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    class_id: Mapped[int | None] = mapped_column(
        ForeignKey("project_classes.id", ondelete="SET NULL"), nullable=True
    )
    # Snapshot of the class name, so history survives a deleted class.
    class_name: Mapped[str] = mapped_column(String(120), index=True)
    image_name: Mapped[str] = mapped_column(String(160))
    index: Mapped[int] = mapped_column(Integer)
    # {format_key: absolute file path}
    files: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    burst_id: Mapped[str] = mapped_column(String(32), index=True)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    depth_scale: Mapped[float] = mapped_column(Float)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    project: Mapped[Project] = relationship()
