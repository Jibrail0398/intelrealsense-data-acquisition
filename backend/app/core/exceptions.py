"""Domain exceptions and the handler that turns them into JSON responses.

Every error the API returns has the shape ``{"error": {"code": ..., "message": ...}}``
so the frontend can show ``message`` directly.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class CameraNotReadyError(AppError):
    status_code = 503
    code = "camera_not_ready"


class CaptureBusyError(AppError):
    status_code = 409
    code = "capture_busy"


class UnavailableError(AppError):
    status_code = 501
    code = "unavailable"


def _error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_error_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        message = first.get("msg", "Invalid request")
        if field:
            message = f"{field}: {message}"
        return JSONResponse(status_code=422, content=_error_body("validation_error", message))
