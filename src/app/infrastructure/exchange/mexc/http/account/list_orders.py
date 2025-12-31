"""
Open orders fetch shim for MEXC.
"""
from datetime import datetime
from typing import Dict, Any

from src.app.infrastructure.external.mexc import mexc_client
from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL


async def list_orders(symbol: str = QRL_USDT_SYMBOL) -> Dict[str, Any]:
    async with mexc_client:
        orders = await mexc_client.get_open_orders(symbol)
    return {
        "success": True,
        "source": "api",
        "symbol": symbol,
        "orders": orders,
        "count": len(orders),
        "timestamp": datetime.now().isoformat(),
    }


__all__ = ["list_orders", "QRL_USDT_SYMBOL"]
