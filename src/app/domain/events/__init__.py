"""
Domain Events Package (Legacy Compatibility)

This package now re-exports from domain.trading for backward compatibility.
New code should import directly from src.app.domain.trading.events.
"""

from src.app.domain.trading.events.trading_events import OrderPlaced, PriceUpdated, TradeExecuted

__all__ = ["OrderPlaced", "PriceUpdated", "TradeExecuted"]

