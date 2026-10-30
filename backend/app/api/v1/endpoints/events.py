from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["events"])


@router.websocket("/events")
async def events(ws: WebSocket) -> None:
    """Realtime events: camera.status, capture.started/progress/completed/failed,
    project.updated/deleted, capture.deleted, camera.config, settings.capture_rules."""
    hub = ws.app.state.hub
    camera = ws.app.state.camera
    await hub.connect(ws)
    try:
        await ws.send_json({"event": "camera.status", "data": camera.status().model_dump(mode="json")})
        while True:
            await ws.receive_text()  # keep-alive pings from the client
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(ws)
