"""
MEXC price fetch shim.

Uses the legacy shared mexc_client to preserve existing behavior.
"""
from datetime import datetime
from typing import Dict

from src.app.infrastructure.external import mexc_client


async def get_price(symbol: str) -> Dict[str, str]:
    async with mexc_client:
        price_data = await mexc_client.get_ticker_price(symbol)
    price = price_data.get("price")
    return {
        "success": True,
        "source": "api",
        "symbol": symbol,
        "price": str(price),
        "timestamp": datetime.now().isoformat(),
    }


__all__ = ["get_price"]
