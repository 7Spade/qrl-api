"""Position model for tracking holdings and costs."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Position:
    total_qrl: float
    core_qrl: float = 0.0
    average_cost: Optional[float] = None
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    last_updated: Optional[datetime] = None


__all__ = ["Position"]
