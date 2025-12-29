import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

# Ensure project root is on sys.path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from api.status import health


class DummyMexcClient:
    async def ping(self):
        return {"ping": True}


class DummyRedisClient:
    def __init__(self, ok=True):
        self.ok = ok
        self.connected = False

    async def connect(self):
        self.connected = True
        return self.ok

    async def health_check(self):
        return self.ok


@pytest.mark.asyncio
async def test_health_reports_missing_credentials(monkeypatch):
    dummy_config = SimpleNamespace(
        FLASK_ENV="prod",
        MEXC_API_KEY=None,
        MEXC_SECRET_KEY=None,
        REDIS_URL="redis://example",
    )
    monkeypatch.setattr(health, "config", dummy_config)
    monkeypatch.setattr(health, "_get_mexc_client", lambda: DummyMexcClient())
    monkeypatch.setattr(health, "_get_redis_client", lambda: DummyRedisClient())

    result = await health.health_check()

    assert result.status == "degraded"
    assert "MEXC_API_KEY" in result.missing
    assert "MEXC_SECRET_KEY" in result.missing
    assert result.redis_connected is True


@pytest.mark.asyncio
async def test_health_reports_healthy_when_dependencies_ok(monkeypatch):
    dummy_config = SimpleNamespace(
        FLASK_ENV="prod",
        MEXC_API_KEY="key",
        MEXC_SECRET_KEY="secret",
        REDIS_URL="redis://example",
    )
    dummy_redis = DummyRedisClient()
    dummy_mexc = DummyMexcClient()

    monkeypatch.setattr(health, "config", dummy_config)
    monkeypatch.setattr(health, "_get_mexc_client", lambda: dummy_mexc)
    monkeypatch.setattr(health, "_get_redis_client", lambda: dummy_redis)

    result = await health.health_check()

    assert result.status == "healthy"
    assert result.mexc_reachable is True
    assert result.redis_connected is True
    assert result.missing == []
