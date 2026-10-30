"""Broadcasts realtime events to every connected WebSocket client.

Events are JSON objects ``{"event": "camera.status", "data": {...}}``.
``publish_threadsafe`` may be called from the camera thread or from sync
endpoints running in FastAPI's threadpool.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

log = logging.getLogger(__name__)


class EventHub:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    async def publish(self, event: str, data: Any) -> None:
        message = json.dumps({"event": event, "data": jsonable_encoder(data)})
        for ws in list(self._clients):
            try:
                await ws.send_text(message)
            except Exception:  # client went away mid-send
                self._clients.discard(ws)

    def publish_threadsafe(self, event: str, data: Any) -> None:
        loop = self._loop
        if loop is None or loop.is_closed():
            return
        try:
            running = asyncio.get_running_loop()
        except RuntimeError:
            running = None
        if running is loop:
            loop.create_task(self.publish(event, data))
        else:
            asyncio.run_coroutine_threadsafe(self.publish(event, data), loop)
