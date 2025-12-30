"""Market trades/klines caching helpers."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from infrastructure.config.config import config

logger = logging.getLogger(__name__)


class MarketTradesCacheMixin:
    """Cache helpers for trades and klines."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_recent_trades(self, symbol: str, trades_data: List[Dict[str, Any]]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:trades:{symbol}"
            data = {
                "symbol": symbol,
                "data": trades_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, config.CACHE_TTL_TRADES, json.dumps(data))
            logger.debug("Cached recent trades for %s", symbol)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to cache recent trades for %s: %s", symbol, exc)
            return False

    async def get_recent_trades(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:trades:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get recent trades for %s: %s", symbol, exc)
            return None

    async def set_klines(self, symbol: str, interval: str, klines_data: List[List[Any]], ttl: int) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:klines:{symbol}:{interval}"
            data = {
                "symbol": symbol,
                "interval": interval,
                "data": klines_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, ttl, json.dumps(data))
            logger.debug("Cached klines for %s %s", symbol, interval)
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to cache klines for %s: %s", symbol, exc)
            return False

    async def get_klines(self, symbol: str, interval: str) -> Optional[List[List[Any]]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:klines:{symbol}:{interval}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error("Failed to get klines for %s: %s", symbol, exc)
            return None


__all__ = ["MarketTradesCacheMixin"]
