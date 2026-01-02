"""Simple trading events used for decoupled messaging."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(slots=True)
class PriceUpdated:
    symbol: str
    price: float
    timestamp: datetime = datetime.utcnow()


@dataclass(slots=True)
class OrderPlaced:
    symbol: str
    side: str
    quantity: float
    price: float | None = None
    metadata: Dict[str, Any] | None = None
    timestamp: datetime = datetime.utcnow()


@dataclass(slots=True)
class TradeExecuted:
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: datetime = datetime.utcnow()


__all__ = ["PriceUpdated", "OrderPlaced", "TradeExecuted"]
