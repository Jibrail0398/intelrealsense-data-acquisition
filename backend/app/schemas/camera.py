from typing import Literal

from pydantic import BaseModel, Field, model_validator

CameraStatusValue = Literal["disconnected", "connecting", "connected", "error"]
Colormap = Literal["turbo", "jet", "inferno", "viridis", "bone"]


class StreamProfile(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    fps: int = Field(gt=0)


class DecimationFilter(BaseModel):
    enabled: bool = False
    magnitude: int = Field(2, ge=2, le=8)


class ThresholdFilter(BaseModel):
    enabled: bool = False
    min_distance: float = Field(0.1, ge=0, le=16)
    max_distance: float = Field(4.0, ge=0, le=16)

    @model_validator(mode="after")
    def _order(self) -> "ThresholdFilter":
        if self.max_distance <= self.min_distance:
            raise ValueError("max_distance must be greater than min_distance")
        return self


class SpatialFilter(BaseModel):
    enabled: bool = False
    magnitude: int = Field(2, ge=1, le=5)
    smooth_alpha: float = Field(0.5, ge=0.25, le=1)
    smooth_delta: int = Field(20, ge=1, le=50)
    holes_fill: int = Field(0, ge=0, le=5)


class TemporalFilter(BaseModel):
    enabled: bool = False
    smooth_alpha: float = Field(0.4, ge=0, le=1)
    smooth_delta: int = Field(20, ge=1, le=100)
    persistence: int = Field(3, ge=0, le=8)


class HoleFillingFilter(BaseModel):
    enabled: bool = False
    # 0 fill from left, 1 farthest from around, 2 nearest from around
    mode: int = Field(1, ge=0, le=2)


class FilterConfig(BaseModel):
    """librealsense post-processing blocks, applied in Intel's recommended order."""

    decimation: DecimationFilter = DecimationFilter()
    threshold: ThresholdFilter = ThresholdFilter()
    disparity_domain: bool = True
    spatial: SpatialFilter = SpatialFilter()
    temporal: TemporalFilter = TemporalFilter()
    hole_filling: HoleFillingFilter = HoleFillingFilter()


class PreviewConfig(BaseModel):
    colormap: Colormap = "turbo"
    min_distance: float = Field(0.2, ge=0, le=16)
    max_distance: float = Field(4.0, ge=0.1, le=16)

    @model_validator(mode="after")
    def _order(self) -> "PreviewConfig":
        if self.max_distance <= self.min_distance:
            raise ValueError("max_distance must be greater than min_distance")
        return self


class CameraConfig(BaseModel):
    color: StreamProfile = StreamProfile(width=640, height=480, fps=30)
    depth: StreamProfile = StreamProfile(width=640, height=480, fps=30)
    align_to_color: bool = True
    filters: FilterConfig = FilterConfig()
    preview: PreviewConfig = PreviewConfig()
    # Option values the user changed, re-applied on every connect:
    # {sensor_key: {option_name: value}}
    options: dict[str, dict[str, float]] = {}

    @model_validator(mode="after")
    def _decimation_vs_align(self) -> "CameraConfig":
        if self.align_to_color and self.filters.decimation.enabled:
            raise ValueError(
                "Decimation shrinks the depth image, so it cannot be used while "
                "depth is aligned to RGB. Turn off alignment first."
            )
        return self


class CameraConfigUpdate(BaseModel):
    color: StreamProfile | None = None
    depth: StreamProfile | None = None
    align_to_color: bool | None = None
    filters: FilterConfig | None = None
    preview: PreviewConfig | None = None


class CameraStatus(BaseModel):
    status: CameraStatusValue
    message: str | None = None
    backend: Literal["realsense", "mock"]
    device: dict[str, str] | None = None
    color: StreamProfile | None = None
    depth: StreamProfile | None = None
    fps: float = 0.0


class ResolutionOption(BaseModel):
    width: int
    height: int
    fps: list[int]


class StreamCapabilities(BaseModel):
    color: list[ResolutionOption]
    depth: list[ResolutionOption]


class OptionChoice(BaseModel):
    value: float
    label: str


class SensorOption(BaseModel):
    name: str
    label: str
    description: str
    value: float
    min: float
    max: float
    step: float
    default: float
    read_only: bool
    kind: Literal["bool", "choice", "range"]
    choices: list[OptionChoice] | None = None


class SensorOptions(BaseModel):
    key: str
    name: str
    options: list[SensorOption]


class SetOptionRequest(BaseModel):
    sensor: str
    option: str
    value: float


class DepthSample(BaseModel):
    x: int
    y: int
    distance_m: float
