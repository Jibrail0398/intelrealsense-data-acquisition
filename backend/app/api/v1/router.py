from fastapi import APIRouter

from app.api.v1.endpoints import camera, capture, events, history, projects, settings, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(projects.router)
api_router.include_router(settings.router)
api_router.include_router(camera.router)
api_router.include_router(capture.router)
api_router.include_router(history.router)
api_router.include_router(events.router)
