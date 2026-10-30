"""Application settings loaded from environment variables and `.env`."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RealSense Dataset Collector"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"

    # auto / realsense -> a physical RealSense camera through pyrealsense2
    # mock             -> synthetic frames, for developing without hardware
    camera_backend: Literal["auto", "realsense", "mock"] = "auto"
    camera_auto_connect: bool = True
    camera_poll_seconds: float = 2.0

    preview_fps: int = 15
    preview_jpeg_quality: int = 80

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
