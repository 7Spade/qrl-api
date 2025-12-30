"""
Websocket connection shims for MEXC streams.
"""

from infrastructure.external.mexc_client import (
    connect_public_trades,
    connect_user_stream,
    websocket_manager,
    MEXCWebSocketClient,
)

__all__ = [
    "connect_public_trades",
    "connect_user_stream",
    "websocket_manager",
    "MEXCWebSocketClient",
]
