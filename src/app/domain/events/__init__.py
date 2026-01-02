"""
Domain Events Package (Legacy Compatibility)

⚠️ DEPRECATED: This module provides backward compatibility only.

New code should use:
    from src.app.domain.trading.events import OrderPlaced, PriceUpdated, TradeExecuted

This backward compatibility layer will be maintained for at least 2 major versions.
"""

import warnings

warnings.warn(
    "domain.events is deprecated. Use domain.trading.events instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.app.domain.trading.events.trading_events import OrderPlaced, PriceUpdated, TradeExecuted

__all__ = ["OrderPlaced", "PriceUpdated", "TradeExecuted"]

