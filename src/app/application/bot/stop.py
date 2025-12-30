"""
Bot stop use case shim re-exporting TradingService.
"""

from services.trading.trading_service_core import TradingService

__all__ = ["TradingService"]
