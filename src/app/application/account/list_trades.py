"""
Account trade-history use case shim.

Re-exports the legacy route handler so downstream code can import from the
new application layer without altering behavior.
"""

from api.account.trades import get_trades

__all__ = ["get_trades"]
