"""Camera configuration: validates, persists and hands changes to the manager."""

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.schemas.camera import CameraConfig, CameraConfigUpdate, SensorOptions, SetOptionRequest
from app.services.camera import CameraManager
from app.services.event_hub import EventHub
from app.services.settings_service import SettingsService


class CameraService:
    def __init__(self, db: Session, camera: CameraManager, hub: EventHub) -> None:
        self.camera = camera
        self.hub = hub
        self.settings = SettingsService(db)

    def config(self) -> CameraConfig:
        return self.camera.config

    def update_config(self, update: CameraConfigUpdate) -> CameraConfig:
        current = self.camera.config
        merged = current.model_dump()
        merged.update(update.model_dump(exclude_none=True))
        try:
            config = CameraConfig.model_validate(merged)
        except ValidationError as exc:
            raise AppError(exc.errors()[0]["msg"].removeprefix("Value error, ")) from exc

        restart = config.color != current.color or config.depth != current.depth
        self.settings.save_camera_config(config)
        self.camera.update_config(config, restart_stream=restart)
        self.hub.publish_threadsafe("camera.config", config)
        return config

    def sensor_options(self) -> list[SensorOptions]:
        device = self.camera.require_connected()
        return device.sensor_options()

    def set_option(self, req: SetOptionRequest) -> list[SensorOptions]:
        device = self.camera.require_connected()
        try:
            device.set_option(req.sensor, req.option, req.value)
        except (ValueError, RuntimeError) as exc:
            raise AppError(str(exc)) from exc

        config = self.camera.config.model_copy(deep=True)
        sensor_values = config.options.setdefault(req.sensor, {})
        sensor_values.pop(req.option, None)  # re-insert so replay order follows the user's order
        sensor_values[req.option] = req.value
        self._store(config)
        return device.sensor_options()

    def reset_options(self) -> list[SensorOptions]:
        device = self.camera.require_connected()
        for sensor in device.sensor_options():
            for opt in sensor.options:
                if opt.read_only or opt.value == opt.default:
                    continue
                try:
                    device.set_option(sensor.key, opt.name, opt.default)
                except (ValueError, RuntimeError):
                    pass
        config = self.camera.config.model_copy(update={"options": {}}, deep=True)
        self._store(config)
        return device.sensor_options()

    def _store(self, config: CameraConfig) -> None:
        self.settings.save_camera_config(config)
        self.camera.update_config(config, restart_stream=False)
