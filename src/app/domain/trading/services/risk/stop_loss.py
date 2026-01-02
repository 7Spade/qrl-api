"""Simple stop-loss guard to align with target architecture."""
from dataclasses import dataclass


@dataclass(slots=True)
class StopLossGuard:
    max_drawdown: float = 0.1

    def should_exit(self, price: float, avg_cost: float) -> bool:
        if avg_cost <= 0:
            return False
        drawdown = (avg_cost - price) / avg_cost
        return drawdown >= self.max_drawdown


__all__ = ["StopLossGuard"]
