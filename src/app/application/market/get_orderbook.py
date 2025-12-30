"""
Order book use case shim.

Re-exports the legacy FastAPI handler for compatibility.
"""

from api.market.orderbook import get_orderbook

__all__ = ["get_orderbook"]
