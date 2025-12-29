import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from infrastructure.external.mexc_client.core import MEXCClient
from infrastructure.external.mexc_client.signer import generate_signature


def test_generate_signature_matches_helper():
    client = MEXCClient(api_key="k", secret_key="secret")
    params = {"b": 2, "a": 1}
    expected = generate_signature("secret", params)
    assert client._generate_signature(params) == expected


@pytest.mark.asyncio
async def test_place_market_order_delegates_to_create_order(monkeypatch):
    client = MEXCClient(api_key="k", secret_key="secret")
    captured = {}

    async def fake_create_order(**kwargs):
        captured.update(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(client, "create_order", fake_create_order)

    result = await client.place_market_order(symbol="QRLUSDT", side="buy", quantity=1.23)

    assert captured["symbol"] == "QRLUSDT"
    assert captured["side"] == "BUY"
    assert captured["order_type"] == "MARKET"
    assert captured["quantity"] == 1.23
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_place_market_order_requires_quantity(monkeypatch):
    client = MEXCClient(api_key="k", secret_key="secret")

    with pytest.raises(ValueError):
        await client.place_market_order(symbol="QRLUSDT", side="buy")
