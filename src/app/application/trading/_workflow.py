"""Trading workflow orchestrator"""
from datetime import datetime
from typing import Dict


class TradingWorkflow:
    def __init__(
        self, price_resolver, balance_resolver, position_updater,
        position_repo, price_repo, trade_repo, cost_repo,
        trading_strategy, risk_manager, position_manager,
    ):
        self.price_resolver = price_resolver
        self.balance_resolver = balance_resolver
        self.position_updater = position_updater
        self.position_repo = position_repo
        self.price_repo = price_repo
        self.trade_repo = trade_repo
        self.cost_repo = cost_repo
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager
        self.position_manager = position_manager

    async def execute(self, symbol: str = "QRLUSDT") -> Dict:
        """Execute trading decision workflow"""
        price = await self.price_resolver.get_current_price(symbol)
        history = await self.price_resolver.get_price_history(price)
        prices = [float(p.get("price", price)) for p in history]

        pos = await self.position_repo.get_position()
        avg_cost = float(pos.get("average_cost", 0)) if pos else 0

        signal = self.trading_strategy.generate_signal(
            price=price, short_prices=prices[-12:],
            long_prices=prices, avg_cost=avg_cost
        )
        if signal == "HOLD":
            return {
                "success": True, "action": "HOLD",
                "reason": "No trading signal",
                "current_price": price, "price": price,
                "quantity": 0,
                "timestamp": datetime.now().isoformat(),
            }

        daily = await self.trade_repo.get_daily_trades()
        last_time = await self.trade_repo.get_last_trade_time()
        layers = await self.position_repo.get_position_layers()
        usdt = await self.balance_resolver.get_usdt_balance()

        risk = self.risk_manager.check_all_risks(
            signal=signal, daily_trades=daily,
            last_trade_time=last_time, position_layers=layers,
            usdt_balance=usdt
        )
        if not risk.get("passed", False):
            return {
                "success": False, "action": signal,
                "reason": f"Risk: {risk.get('reason')}",
                "current_price": price,
                "timestamp": datetime.now().isoformat(),
            }

        qty = await self._calc_qty(signal, pos, usdt, price)
        if qty <= 0:
            return {
                "success": False, "action": signal,
                "reason": "Insufficient quantity",
                "current_price": price,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "success": True, "action": signal, "quantity": qty,
            "price": price,
            "timestamp": datetime.now().isoformat(),
        }

    async def _calc_qty(self, signal, pos, usdt, price):
        if signal == "BUY":
            r = self.position_manager.calculate_buy_quantity(
                usdt_balance=usdt, price=price
            )
            return r.get("quantity", 0)
        total = float(pos.get("total_qrl", 0)) if pos else 0
        core = float(pos.get("core_qrl", 0)) if pos else 0
        r = self.position_manager.calculate_sell_quantity(
            total_qrl=total, core_qrl=core
        )
        return r.get("quantity", 0)

