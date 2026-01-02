"""Price snapshot model used across application services."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Price:
    symbol: str
    value: float
    change_percent: Optional[float] = None
    volume_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: datetime = datetime.utcnow()


__all__ = ["Price"]
