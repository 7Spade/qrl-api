"""
Domain Strategies Package (Legacy Compatibility)

⚠️ DEPRECATED: This module provides backward compatibility only.

New code should use:
    from src.app.domain.trading.strategies import BaseStrategy, TradingStrategy

This backward compatibility layer will be maintained for at least 2 major versions.
"""

import warnings

warnings.warn(
    "domain.strategies is deprecated. Use domain.trading.strategies instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.app.domain.trading.strategies.base import BaseStrategy
from src.app.domain.trading.strategies.example_strategy import ExampleStrategy
from src.app.domain.trading.strategies.trading_strategy import TradingStrategy

__all__ = ["BaseStrategy", "ExampleStrategy", "TradingStrategy"]

