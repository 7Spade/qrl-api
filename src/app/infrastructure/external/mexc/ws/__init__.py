"""MEXC WebSocket client."""
from src.app.infrastructure.external.mexc.ws.client import MEXCWebSocketClient
from src.app.infrastructure.external.mexc.ws.channels import (
    diff_depth_stream,
    partial_depth_stream,
    trade_stream,
    kline_stream,
    account_update_stream,
)

__all__ = [
    "MEXCWebSocketClient",
    "diff_depth_stream",
    "partial_depth_stream",
    "trade_stream",
    "kline_stream",
    "account_update_stream",
]
