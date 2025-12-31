"""
Bot status use case shim.

Re-exports TradingService to keep status-related helpers accessible from the
new application layer.
"""

from src.app.application.trading.services import TradingService

__all__ = ["TradingService"]
