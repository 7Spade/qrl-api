"""
Cancel order shim leveraging the legacy mexc_client implementation.
"""
from typing import Any, Dict, Optional

from src.app.infrastructure.external import mexc_client


async def cancel_order(
    symbol: str,
    order_id: Optional[int] = None,
    orig_client_order_id: Optional[str] = None,
) -> Dict[str, Any]:
    async with mexc_client:
        return await mexc_client.cancel_order(
            symbol=symbol,
            order_id=order_id,
            orig_client_order_id=orig_client_order_id,
        )


__all__ = ["cancel_order"]
