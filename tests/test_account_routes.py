import sys
from pathlib import Path
import importlib

import pytest
from fastapi import HTTPException

# Ensure project root is on sys.path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from api import account_routes
from infrastructure.external.mexc_client.account import fetch_balance_snapshot

mexc_module = importlib.import_module("infrastructure.external.mexc_client")
redis_module = importlib.import_module("infrastructure.external.redis_client")


class DummyMexcClient:
    def __init__(self) -> None:
        self.account_called = False
        self.price_called = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_account_info(self):
        self.account_called = True
        return {
            "balances": [
                {"asset": "QRL", "free": "2", "locked": "3"},
                {"asset": "USDT", "free": "5", "locked": "1"},
            ],
            "accountType": "SPOT",
            "canTrade": True,
        }

    async def get_ticker_price(self, symbol: str):
        self.price_called = True
        return {"symbol": symbol, "price": "0.5"}

    async def get_balance_snapshot(self):
        return await fetch_balance_snapshot(self)


class DummyMexcClientMissingPrice(DummyMexcClient):
    async def get_ticker_price(self, symbol: str):
        self.price_called = True
        return {"symbol": symbol, "price": None}


@pytest.mark.asyncio
async def test_balance_includes_qrl_value(monkeypatch):
    dummy_client = DummyMexcClient()
    monkeypatch.setattr(mexc_module, "mexc_client", dummy_client)

    result = await account_routes.get_account_balance()

    assert dummy_client.account_called is True
    assert dummy_client.price_called is True
    assert result["balances"]["QRL"]["total"] == 5.0
    assert result["balances"]["QRL"]["value_usdt"] == pytest.approx(2.5)
    assert result["prices"]["QRLUSDT"] == 0.5
    assert result["balances"]["USDT"]["total"] == 6.0


@pytest.mark.asyncio
async def test_balance_requires_price(monkeypatch):
    dummy_client = DummyMexcClientMissingPrice()
    monkeypatch.setattr(mexc_module, "mexc_client", dummy_client)

    with pytest.raises(HTTPException):
        await account_routes.get_account_balance()


class DummyRedisClient:
    def __init__(self) -> None:
        self.calls = []

    async def get_mexc_raw_response(self, endpoint: str):
        self.calls.append(endpoint)
        return {"endpoint": endpoint, "data": {"foo": "bar"}}

    async def get_mexc_account_balance(self):
        return {"balances": {"QRL": {"total": "1"}, "USDT": {"total": "2"}}}

    async def get_mexc_qrl_price(self):
        return {"price": "0.5", "price_float": 0.5}

    async def get_mexc_total_value(self):
        return {"total_value_usdt": "2.5", "total_value_float": 2.5}


class EmptyRedisClient:
    async def get_mexc_raw_response(self, endpoint: str):
        return None

    async def get_mexc_account_balance(self):
        return None

    async def get_mexc_qrl_price(self):
        return None

    async def get_mexc_total_value(self):
        return None


@pytest.mark.asyncio
async def test_balance_redis_returns_data(monkeypatch):
    dummy_redis = DummyRedisClient()
    monkeypatch.setattr(redis_module, "redis_client", dummy_redis)

    result = await account_routes.get_balance_redis()

    assert result["source"] == "redis"
    assert result["raw"]["endpoint"] == "account_balance"
    assert result["price"]["price"] == "0.5"
    assert dummy_redis.calls == ["account_balance"]


@pytest.mark.asyncio
async def test_balance_redis_missing_data(monkeypatch):
    monkeypatch.setattr(redis_module, "redis_client", EmptyRedisClient())

    with pytest.raises(HTTPException):
        await account_routes.get_balance_redis()
