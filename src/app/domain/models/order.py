"""Order value object for domain workflows.

Lightweight dataclass to keep architecture tree aligned without changing
runtime behavior. Fields mirror the data returned by exchange adapters.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Order:
    symbol: str
    side: str
    quantity: float
    price: Optional[float] = None
    order_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


__all__ = ["Order"]
