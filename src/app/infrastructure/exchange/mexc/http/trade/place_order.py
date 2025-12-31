"""
Place order shim leveraging the legacy mexc_client implementation.
"""
from typing import Any, Dict, Optional

from src.app.infrastructure.external import mexc_client


async def place_order(
    symbol: str,
    side: str,
    order_type: str = "MARKET",
    quantity: Optional[float] = None,
    quote_order_qty: Optional[float] = None,
    price: Optional[float] = None,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    async with mexc_client:
        return await mexc_client.create_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            quote_order_qty=quote_order_qty,
            price=price,
            time_in_force=time_in_force,
        )


__all__ = ["place_order"]
