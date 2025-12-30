"""Example strategy shim that reuses the legacy implementation."""
from domain.trading_strategy.core import TradingStrategy as LegacyTradingStrategy

from src.app.domain.strategies.base import BaseStrategy


class ExampleStrategy(LegacyTradingStrategy, BaseStrategy):
    """Concrete strategy that defers to the legacy TradingStrategy logic."""


__all__ = ["ExampleStrategy"]
