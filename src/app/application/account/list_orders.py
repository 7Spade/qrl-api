"""
Account open-orders use case shim.

Re-exports the existing FastAPI handler for compatibility during
progressive migration.
"""

from api.account.orders import get_orders

__all__ = ["get_orders"]
