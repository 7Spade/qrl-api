"""
Bot status use case shim.

Re-exports TradingService to keep status-related helpers accessible from the
new application layer.
"""

from services.trading.trading_service_core import TradingService

__all__ = ["TradingService"]
