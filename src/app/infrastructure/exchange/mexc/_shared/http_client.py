"""
HTTP client shim for MEXC exchange access.

Re-exports the legacy MexcConnection used by `infrastructure.external.mexc_client`.
"""

from infrastructure.external.mexc_client.connection import MexcConnection

__all__ = ["MexcConnection"]
