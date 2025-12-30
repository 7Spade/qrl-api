"""
Kline history use case shim.

Delegates to the legacy handler to avoid behavior changes during migration.
"""

from api.market.klines import get_klines

__all__ = ["get_klines"]
