"""
Compatibility shim for TradingService.
Delegates to services.trading.trading_service to keep imports stable
after restructuring the service package per README layout.
"""
from services.trading.trading_service import TradingService

__all__ = ["TradingService"]
