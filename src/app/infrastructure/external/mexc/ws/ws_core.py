"""Backward compatible websocket core import."""
import websockets

from src.app.infrastructure.external.mexc.websocket.client import (
    MEXCWebSocketClient,
    WS_BASE,
)

__all__ = ["MEXCWebSocketClient", "WS_BASE", "websockets"]
