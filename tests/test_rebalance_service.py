import pytest

from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)


class _DummyBalanceService:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    async def get_account_balance(self):
        return self.snapshot


class _DummyRedis:
    def __init__(self):
        self.saved = None

    async def set_rebalance_plan(self, plan):
        self.saved = plan
        return True


def _snapshot(qrl_total: float, usdt_total: float, price: float):
    return {
        "balances": {
            "QRL": {"total": qrl_total, "price": price},
            "USDT": {"total": usdt_total},
        },
        "prices": {"QRLUSDT": price},
    }


@pytest.mark.asyncio
async def test_rebalance_buy():
    snapshot = _snapshot(qrl_total=10, usdt_total=80, price=2)
    redis = _DummyRedis()
    service = RebalanceService(
        _DummyBalanceService(snapshot),
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )
    plan = await service.generate_plan(snapshot)

    assert plan["action"] == "BUY"
    assert pytest.approx(plan["quantity"], rel=1e-3) == 15
    assert redis.saved["action"] == "BUY"


@pytest.mark.asyncio
async def test_rebalance_sell():
    snapshot = _snapshot(qrl_total=50, usdt_total=20, price=2)
    service = RebalanceService(
        _DummyBalanceService(snapshot),
        _DummyRedis(),
        min_notional_usdt=0.1,
        threshold_pct=0,
    )
    plan = await service.generate_plan(snapshot)

    assert plan["action"] == "SELL"
    assert pytest.approx(plan["quantity"], rel=1e-3) == 20


@pytest.mark.asyncio
async def test_rebalance_hold_within_threshold():
    snapshot = _snapshot(qrl_total=25, usdt_total=50, price=2)
    service = RebalanceService(
        _DummyBalanceService(snapshot),
        _DummyRedis(),
        min_notional_usdt=1,
        threshold_pct=0.05,
    )
    plan = await service.generate_plan(snapshot)

    assert plan["action"] == "HOLD"
    assert plan["reason"] == "Within threshold"
