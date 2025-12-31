"""
Market adapter shim exposing the legacy MEXCClient.
"""

from src.app.infrastructure.external.mexc import MEXCClient, mexc_client

__all__ = ["MEXCClient", "mexc_client"]
