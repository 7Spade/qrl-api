"""
Domain Strategies Package (Legacy Compatibility)

This package now re-exports from domain.trading for backward compatibility.
New code should import directly from src.app.domain.trading.strategies.
"""

from src.app.domain.trading.strategies.base import BaseStrategy
from src.app.domain.trading.strategies.example_strategy import ExampleStrategy
from src.app.domain.trading.strategies.trading_strategy import TradingStrategy

__all__ = ["BaseStrategy", "ExampleStrategy", "TradingStrategy"]

