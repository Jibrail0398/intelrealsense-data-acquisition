import asyncio

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from app.api.deps import Camera, CameraSvc
from app.core.config import get_settings
from app.core.exceptions import AppError, CameraNotReadyError
from app.schemas.camera import (
    CameraConfig,
    CameraConfigUpdate,
    CameraStatus,
    DepthSample,
    SensorOptions,
    SetOptionRequest,
    StreamCapabilities,
)

router = APIRouter(prefix="/camera", tags=["camera"])

_BOUNDARY = "frame"


@router.get("/status", response_model=CameraStatus)
def camera_status(camera: Camera) -> CameraStatus:
    return camera.status()


@router.post("/connect", response_model=CameraStatus)
def connect(camera: Camera) -> CameraStatus:
    camera.connect()
    return camera.status()


@router.post("/disconnect", response_model=CameraStatus)
def disconnect(camera: Camera) -> CameraStatus:
    camera.disconnect()
    return camera.status()


@router.post("/reset", response_model=CameraStatus)
def hardware_reset(camera: Camera) -> CameraStatus:
    try:
        camera.hardware_reset()
    except RuntimeError as exc:
        raise AppError(str(exc)) from exc
    return camera.status()


@router.get("/capabilities", response_model=StreamCapabilities)
def capabilities(camera: Camera) -> StreamCapabilities:
    device = camera.require_device()
    try:
        return device.capabilities()
    except RuntimeError as exc:
        raise CameraNotReadyError(str(exc)) from exc


@router.get("/config", response_model=CameraConfig)
def get_config(service: CameraSvc) -> CameraConfig:
    return service.config()


@router.put("/config", response_model=CameraConfig)
def update_config(update: CameraConfigUpdate, service: CameraSvc) -> CameraConfig:
    return service.update_config(update)


@router.get("/options", response_model=list[SensorOptions])
def sensor_options(service: CameraSvc) -> list[SensorOptions]:
    return service.sensor_options()


@router.put("/options", response_model=list[SensorOptions])
def set_option(req: SetOptionRequest, service: CameraSvc) -> list[SensorOptions]:
    return service.set_option(req)


@router.post("/options/reset", response_model=list[SensorOptions])
def reset_options(service: CameraSvc) -> list[SensorOptions]:
    return service.reset_options()


@router.get("/depth", response_model=DepthSample)
def depth_at(camera: Camera, x: int = Query(ge=0), y: int = Query(ge=0)) -> DepthSample:
    frame = camera.latest()
    if frame is None:
        raise CameraNotReadyError("No frame yet")
    h, w = frame.depth.shape[:2]
    if x >= w or y >= h:
        raise AppError(f"Pixel is outside the {w}x{h} depth image")
    return DepthSample(x=x, y=y, distance_m=round(float(frame.depth[y, x]) * frame.depth_scale, 4))


@router.get("/stream/{kind}")
async def stream(kind: str, request: Request, camera: Camera) -> StreamingResponse:
    """MJPEG stream; use it as the `src` of an <img>."""
    if kind not in ("rgb", "depth"):
        raise AppError("Stream must be rgb or depth")
    period = 1 / max(get_settings().preview_fps, 1)

    async def frames():
        last_seq = -1
        while not await request.is_disconnected():
            entry = camera.preview_jpeg(kind)
            if entry and entry[0] != last_seq:
                last_seq, jpeg = entry
                yield (
                    f"--{_BOUNDARY}\r\nContent-Type: image/jpeg\r\nContent-Length: {len(jpeg)}\r\n\r\n".encode()
                    + jpeg + b"\r\n"
                )
            await asyncio.sleep(period)

    return StreamingResponse(
        frames(),
        media_type=f"multipart/x-mixed-replace; boundary={_BOUNDARY}",
        headers={"Cache-Control": "no-store"},
    )
