"""
HTTP client shim for MEXC exchange access.

Re-exports the legacy MexcConnection used by `infrastructure.external.mexc_client`.
"""

from src.app.infrastructure.external.mexc.connection import MexcConnection

__all__ = ["MexcConnection"]
