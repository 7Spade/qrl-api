"""
Order book fetch shim aligned with the target infrastructure layout.
"""
from datetime import datetime
from typing import Dict

from src.app.infrastructure.external import mexc_client


async def get_orderbook(symbol: str, limit: int = 50) -> Dict[str, object]:
    async with mexc_client:
        orderbook = await mexc_client.get_order_book(symbol, limit)
    return {
        "success": True,
        "source": "api",
        "symbol": symbol,
        "data": orderbook,
        "timestamp": datetime.now().isoformat(),
    }


__all__ = ["get_orderbook"]
