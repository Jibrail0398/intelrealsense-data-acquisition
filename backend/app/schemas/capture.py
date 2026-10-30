from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.utils.time import as_utc


class CaptureRequest(BaseModel):
    project_id: int
    class_id: int
    # Overrides of the saved capture rules; omitted -> use the rules.
    images_per_take: int | None = Field(None, ge=1, le=100)
    burst_interval_ms: int | None = Field(None, ge=0, le=10_000)


class CaptureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    project_name: str = ""
    class_id: int | None
    class_name: str
    image_name: str
    index: int
    files: dict[str, str]
    burst_id: str
    width: int
    height: int
    depth_scale: float
    captured_at: datetime

    @field_serializer("captured_at")
    def _utc(self, value: datetime) -> str:
        return as_utc(value).isoformat().replace("+00:00", "Z")


class CaptureResult(BaseModel):
    burst_id: str
    captures: list[CaptureOut]


class NextName(BaseModel):
    image_name: str
    index: int
    paths: dict[str, str]


class HistoryPage(BaseModel):
    items: list[CaptureOut]
    total: int
    limit: int
    offset: int
