"""
Market adapter shim exposing the legacy MEXCClient.
"""

from infrastructure.external.mexc_client import MEXCClient, mexc_client

__all__ = ["MEXCClient", "mexc_client"]
