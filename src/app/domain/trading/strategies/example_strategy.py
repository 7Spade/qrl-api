"""Example strategy shim that reuses the legacy implementation."""
from src.app.domain.trading.strategies.trading_strategy import TradingStrategy as LegacyTradingStrategy

from src.app.domain.trading.strategies.base import BaseStrategy


class ExampleStrategy(LegacyTradingStrategy, BaseStrategy):
    """Concrete strategy that defers to the legacy TradingStrategy logic."""


__all__ = ["ExampleStrategy"]
