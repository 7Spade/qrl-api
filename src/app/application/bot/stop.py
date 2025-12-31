"""
Bot stop use case shim re-exporting TradingService.
"""

from src.app.application.trading.services import TradingService

__all__ = ["TradingService"]
