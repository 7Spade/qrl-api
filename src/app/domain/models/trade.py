"""Trade record model used for persistence and reporting."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Trade:
    symbol: str
    side: str
    quantity: float
    price: float
    trade_id: Optional[str] = None
    order_id: Optional[str] = None
    executed_at: datetime = datetime.utcnow()


__all__ = ["Trade"]
