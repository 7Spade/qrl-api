"""Helpers to update position state after trades."""
from __future__ import annotations

from src.app.domain.models.position import Position
from src.app.domain.position.calculator import PositionManager


class PositionUpdater:
    def __init__(self, calculator: PositionManager | None = None) -> None:
        self.calculator = calculator or PositionManager()

    def apply_buy(self, position: Position, quantity: float, price: float) -> Position:
        totals = self.calculator.calculate_new_average_cost(
            old_avg_cost=position.average_cost or price,
            old_total_invested=(position.average_cost or 0) * position.total_qrl,
            qrl_balance=position.total_qrl,
            buy_price=price,
            buy_quantity=quantity,
            usdt_spent=price * quantity,
        )
        return Position(
            total_qrl=totals["new_qrl_balance"],
            core_qrl=position.core_qrl,
            average_cost=totals["new_avg_cost"],
            realized_pnl=position.realized_pnl,
            unrealized_pnl=position.unrealized_pnl,
        )

    def apply_sell(self, position: Position, quantity: float, price: float) -> Position:
        pnl = self.calculator.calculate_pnl_after_sell(
            avg_cost=position.average_cost or 0,
            sell_price=price,
            sell_quantity=quantity,
            qrl_balance=position.total_qrl,
            old_realized_pnl=position.realized_pnl,
        )
        return Position(
            total_qrl=pnl["new_qrl_balance"],
            core_qrl=position.core_qrl,
            average_cost=pnl.get("avg_cost"),
            realized_pnl=pnl.get("new_realized_pnl", position.realized_pnl),
            unrealized_pnl=pnl.get("unrealized_pnl", position.unrealized_pnl),
        )


__all__ = ["PositionUpdater"]
