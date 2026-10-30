from typing import Literal

from pydantic import BaseModel, Field

TimerSeconds = Literal[0, 3, 5, 10, 20]


class CaptureRules(BaseModel):
    images_per_take: int = Field(1, ge=1, le=100)
    burst_interval_ms: int = Field(200, ge=0, le=10_000)
    timer_seconds: TimerSeconds = 0


class SessionState(BaseModel):
    active_project_id: int | None = None
    active_class_id: int | None = None
