"""
Price and valuation caching helpers split from BalanceCacheMixin.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BalancePriceCacheMixin:
    """Mixin providing price and valuation caching helpers."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_mexc_qrl_price(self, price: float, price_data: Optional[Dict[str, Any]] = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:qrl_price"
            payload = {
                "price": str(price),
                "price_float": price,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            if price_data:
                payload["raw_data"] = price_data
            await client.set(key, json.dumps(payload))
            logger.info("Stored QRL price: %s USDT", price)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to store QRL price: %s", exc)
            return False

    async def get_mexc_qrl_price(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:qrl_price"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get QRL price: %s", exc)
            return None

    async def set_mexc_total_value(self, total_value_usdt: float, breakdown: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:total_value"
            payload = {
                "total_value_usdt": str(total_value_usdt),
                "total_value_float": total_value_usdt,
                "breakdown": breakdown,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            await client.set(key, json.dumps(payload))
            logger.info("Stored total account value: %s USDT", total_value_usdt)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to store total value: %s", exc)
            return False

    async def get_mexc_total_value(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:total_value"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get total value: %s", exc)
            return None


__all__ = ["BalancePriceCacheMixin"]
