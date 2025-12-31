"""
Symmetric rebalance planner (equal QRL/USDT value target).

Rules:
- Target portfolio value split: QRL value 50%, USDT 50% (symmetric).
- HOLD when total value is zero/price missing, below min notional, or deviation
  is below threshold_pct of total value.
- SELL when QRL value is above target; clamp to current QRL balance.
- BUY when QRL value is below target; clamp to available USDT.
- The planner only computes and records intent; it does not place orders.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from src.app.infrastructure.external import QRL_USDT_SYMBOL
from src.app.infrastructure.utils import safe_float


class RebalanceService:
    def __init__(
        self,
        balance_service,
        redis_client=None,
        target_ratio: float = 0.5,
        min_notional_usdt: float = 5.0,
        threshold_pct: float = 0.01,
    ) -> None:
        self.balance_service = balance_service
        self.redis = redis_client
        self.target_ratio = target_ratio
        self.min_notional_usdt = min_notional_usdt
        self.threshold_pct = threshold_pct

    async def generate_plan(
        self, snapshot: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a rebalance plan based on live or provided balances.
        """
        snapshot = snapshot or await self.balance_service.get_account_balance()
        plan = self.compute_plan(snapshot)
        await self._record_plan(plan)
        return plan

    def compute_plan(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pure calculation for deterministic testing.
        """
        qrl_data = snapshot.get("balances", {}).get("QRL", {})
        usdt_data = snapshot.get("balances", {}).get("USDT", {})
        price_entry = snapshot.get("prices", {}).get(QRL_USDT_SYMBOL)
        price = safe_float(price_entry or qrl_data.get("price"))

        qrl_total = safe_float(qrl_data.get("total", 0))
        usdt_total = safe_float(usdt_data.get("total", 0))

        total_value = qrl_total * price + usdt_total
        target_value = total_value * self.target_ratio
        qrl_value = qrl_total * price
        delta = qrl_value - target_value
        notional = abs(delta)
        quantity = notional / price if price > 0 else 0

        plan: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "qrl_balance": qrl_total,
            "usdt_balance": usdt_total,
            "qrl_value_usdt": qrl_value,
            "usdt_value_usdt": usdt_total,
            "total_value_usdt": total_value,
            "target_value_usdt": target_value,
            "target_ratio": self.target_ratio,
            "quantity": quantity,
            "notional_usdt": notional,
        }

        if price <= 0 or total_value <= 0:
            plan.update({"action": "HOLD", "reason": "Insufficient price or balance"})
            return plan

        if notional < self.min_notional_usdt or (
            total_value > 0 and (notional / total_value) < self.threshold_pct
        ):
            plan.update({"action": "HOLD", "reason": "Within threshold"})
            return plan

        if delta > 0:
            sell_qty = min(quantity, qrl_total)
            plan.update(
                {
                    "action": "SELL",
                    "reason": "QRL above target",
                    "quantity": sell_qty,
                    "notional_usdt": sell_qty * price,
                }
            )
        else:
            buy_qty = min(quantity, usdt_total / price if price > 0 else 0)
            if buy_qty <= 0:
                plan.update({"action": "HOLD", "reason": "Insufficient USDT"})
                return plan
            plan.update(
                {
                    "action": "BUY",
                    "reason": "QRL below target",
                    "quantity": buy_qty,
                    "notional_usdt": buy_qty * price,
                }
            )
        return plan

    async def _record_plan(self, plan: Dict[str, Any]) -> None:
        if not self.redis or not hasattr(self.redis, "set_rebalance_plan"):
            return
        try:
            await self.redis.set_rebalance_plan(plan)
        except Exception:
            # Best-effort logging only
            pass


__all__ = ["RebalanceService"]
