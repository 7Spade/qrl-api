"""MEXC API client for spot trading."""
from src.app.infrastructure.external.mexc.client import MEXCClient, mexc_client
from src.app.infrastructure.external.mexc.exceptions import MEXCAPIException
from src.app.infrastructure.external.mexc.ws.channels import (
    diff_depth_stream,
    partial_depth_stream,
    trade_stream,
    kline_stream,
    account_update_stream,
)

__all__ = [
    "MEXCClient",
    "mexc_client",
    "MEXCAPIException",
    "diff_depth_stream",
    "partial_depth_stream",
    "trade_stream",
    "kline_stream",
    "account_update_stream",
]
