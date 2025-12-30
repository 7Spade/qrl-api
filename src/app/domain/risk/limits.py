"""
Risk management domain logic (migrated).

Preserves existing behavior while relocating under `src/app/domain`.
"""

from typing import Any, Dict
import time

from src.app.infrastructure.config.env import config


class RiskManager:
    """
    Risk control for trading operations.
    """

    def __init__(
        self,
        max_daily_trades: int | None = None,
        min_trade_interval: int | None = None,
        core_position_pct: float | None = None,
    ) -> None:
        self.max_daily_trades = max_daily_trades or config.config.MAX_DAILY_TRADES
        self.min_trade_interval = min_trade_interval or config.config.MIN_TRADE_INTERVAL
        self.core_position_pct = core_position_pct or config.config.CORE_POSITION_PCT

    def check_daily_limit(self, daily_trades: int) -> Dict[str, Any]:
        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({daily_trades}/{self.max_daily_trades})",
            }
        return {"allowed": True, "reason": "Daily limit OK"}

    def check_trade_interval(self, last_trade_time: int) -> Dict[str, Any]:
        if not last_trade_time:
            return {"allowed": True, "reason": "No previous trade"}

        elapsed = int(time.time()) - last_trade_time
        if elapsed < self.min_trade_interval:
            return {
                "allowed": False,
                "reason": f"Trade interval too short ({elapsed}s < {self.min_trade_interval}s)",
            }
        return {"allowed": True, "reason": "Trade interval OK"}

    def check_sell_protection(self, position_layers: Dict[str, Any]) -> Dict[str, Any]:
        if not position_layers:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No position layers data",
            }

        total_qrl = float(position_layers.get("total_qrl", 0))
        core_qrl = float(position_layers.get("core_qrl", 0))
        tradeable_qrl = total_qrl - core_qrl

        if tradeable_qrl <= 0:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No tradeable QRL (all in core position)",
            }

        return {
            "allowed": True,
            "tradeable_qrl": tradeable_qrl,
            "reason": "Tradeable QRL available",
        }

    def check_buy_protection(self, usdt_balance: float) -> Dict[str, Any]:
        if usdt_balance <= 0:
            return {"allowed": False, "reason": "Insufficient USDT balance"}
        return {"allowed": True, "reason": "Sufficient USDT"}

    def check_all_risks(
        self,
        signal: str,
        daily_trades: int,
        last_trade_time: int,
        position_layers: Dict[str, Any],
        usdt_balance: float,
    ) -> Dict[str, Any]:
        limit_check = self.check_daily_limit(daily_trades)
        if not limit_check["allowed"]:
            return limit_check

        interval_check = self.check_trade_interval(last_trade_time)
        if not interval_check["allowed"]:
            return interval_check

        if signal == "SELL":
            protection = self.check_sell_protection(position_layers)
            if not protection["allowed"]:
                return protection
        elif signal == "BUY":
            protection = self.check_buy_protection(usdt_balance)
            if not protection["allowed"]:
                return protection

        return {
            "allowed": True,
            "reason": "All risk checks passed",
            "daily_trades": daily_trades,
        }


__all__ = ["RiskManager"]
