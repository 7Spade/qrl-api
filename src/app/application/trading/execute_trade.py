"""
Trading execution use case shim.

Re-exports the legacy TradingService so callers can resolve it from the new
application layer without changing behavior.
"""

from src.app.application.trading.services import TradingService

__all__ = ["TradingService"]
