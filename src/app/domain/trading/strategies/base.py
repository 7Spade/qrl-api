"""Base strategy contract for trading decisions."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseStrategy(Protocol):
    """Contract for trading strategies used by the application layer."""

    def generate_signal(
        self, price: float, short_prices: list[float], long_prices: list[float], avg_cost: float
    ) -> str:  # pragma: no cover - interface only
        ...


__all__ = ["BaseStrategy"]
