"""FastAPI entry point: `uvicorn app.main:app --reload` from the backend folder."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.session import SessionLocal, init_db
from app.services.camera import CameraManager
from app.services.event_hub import EventHub
from app.services.settings_service import SettingsService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    init_db()

    with SessionLocal() as db:
        camera_config = SettingsService(db).camera_config()

    hub = EventHub()
    hub.bind_loop(asyncio.get_running_loop())
    camera = CameraManager(settings, hub, camera_config)
    app.state.hub = hub
    app.state.camera = camera
    camera.start()
    try:
        yield
    finally:
        camera.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
