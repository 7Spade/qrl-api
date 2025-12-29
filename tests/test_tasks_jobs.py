import json
import pytest

from infrastructure.tasks.jobs.balance_job import run_balance_job
from infrastructure.tasks.jobs.price_job import run_price_job


class FakeRedis:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.client = self
        self.store: dict[str, str] = {}

    async def setex(self, key, ttl, value):
        if self.fail:
            raise RuntimeError("redis-down")
        self.store[key] = value

    async def set(self, key, value, ex=None):
        if self.fail:
            raise RuntimeError("redis-down")
        self.store[key] = value

    async def get(self, key):
        if self.fail:
            raise RuntimeError("redis-down")
        return self.store.get(key)

    async def incr(self, key):
        if self.fail:
            raise RuntimeError("redis-down")
        self.store[key] = str(int(self.store.get(key, "0")) + 1)
        return self.store[key]


class FakeMexc:
    def __init__(self, account_info=None, ticker_price=None, ticker_24hr=None, raise_timeout: bool = False):
        self.account_info = account_info or {"balances": []}
        self.ticker_price = ticker_price
        self.ticker_24hr = ticker_24hr
        self.raise_timeout = raise_timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_account_info(self):
        if self.raise_timeout:
            raise TimeoutError("timeout")
        return self.account_info

    async def get_ticker_price(self, symbol: str):
        if self.raise_timeout:
            raise TimeoutError("timeout")
        return {"price": self.ticker_price}

    async def get_ticker_24hr(self, symbol: str):
        if self.raise_timeout:
            raise TimeoutError("timeout")
        return self.ticker_24hr or {
            "lastPrice": self.ticker_price,
            "volume": "1",
            "priceChangePercent": "0",
            "highPrice": self.ticker_price,
            "lowPrice": self.ticker_price,
        }


@pytest.mark.asyncio
async def test_balance_job_price_missing_returns_partial():
    redis = FakeRedis()
    mexc = FakeMexc(
        account_info={"balances": [{"asset": "QRL", "free": "1", "locked": "0"}, {"asset": "USDT", "free": "2", "locked": "0"}]},
        ticker_price=None,
    )
    result = await run_balance_job(redis_override=redis, mexc_override=mexc, request_id="p1")
    assert result["status"] == "partial"
    assert result["data"]["metadata"].get("price_missing") is True


@pytest.mark.asyncio
async def test_price_job_handles_redis_failure():
    redis = FakeRedis(fail=True)
    mexc = FakeMexc(ticker_price="0.1")
    result = await run_price_job(redis_override=redis, mexc_override=mexc, request_id="p2")
    assert result["status"] in {"success", "partial", "degraded"}


@pytest.mark.asyncio
async def test_balance_job_timeout_uses_fallback_cache():
    redis = FakeRedis()
    fallback = {"balances": {"QRL": {"free": "1", "locked": "0", "total": 1}, "USDT": {"free": "0", "locked": "0", "total": 0}}, "prices": {}, "metadata": {}}
    await redis.set("mexc:balance:last", json.dumps(fallback))
    mexc = FakeMexc(raise_timeout=True)
    result = await run_balance_job(redis_override=redis, mexc_override=mexc, request_id="p3")
    assert result["status"] == "degraded"
    assert result["data"]["metadata"].get("source") == "fallback"
