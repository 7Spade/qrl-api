"""
Market price use case shim.

Re-exports the legacy price handler to keep behavior stable while the
application layer takes ownership of the use case.
"""

from api.market.price import get_price

__all__ = ["get_price"]
