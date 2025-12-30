"""Market ticker/order book caching helpers."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from infrastructure.config.config import config

logger = logging.getLogger(__name__)


class MarketPriceCacheMixin:
    """Cache helpers for ticker and order book data."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_ticker_24hr(self, symbol: str, ticker_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:ticker:{symbol}"
            data = {
                "symbol": symbol,
                "data": ticker_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, config.CACHE_TTL_TICKER, json.dumps(data))
            logger.debug("Cached ticker data for %s", symbol)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to cache ticker data for %s: %s", symbol, exc)
            return False

    async def get_ticker_24hr(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:ticker:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get ticker data for %s: %s", symbol, exc)
            return None

    async def set_orderbook(self, symbol: str, orderbook_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:orderbook:{symbol}"
            data = {
                "symbol": symbol,
                "data": orderbook_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, config.CACHE_TTL_ORDER_BOOK, json.dumps(data))
            logger.debug("Cached order book for %s", symbol)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to cache order book for %s: %s", symbol, exc)
            return False

    async def get_orderbook(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:orderbook:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get order book for %s: %s", symbol, exc)
            return None


__all__ = ["MarketPriceCacheMixin"]
