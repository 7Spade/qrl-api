"""
Account balance caching helpers split from BalanceCacheMixin.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AccountBalanceCacheMixin:
    """Mixin providing balance caching helpers."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_mexc_account_balance(self, balance_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:account_balance"
            payload = {
                "balances": balance_data,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            await client.set(key, json.dumps(payload))
            logger.info("Stored MEXC account balance data")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to store MEXC account balance: {exc}")
            return False

    async def get_mexc_account_balance(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:account_balance"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get MEXC account balance: {exc}")
            return None

    async def set_cached_account_balance(self, balance_data: Dict[str, Any], ttl: int = 45) -> bool:
        """Store short-lived balance snapshot for UI stability."""
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:account_balance:cache"
            payload = {
                **balance_data,
                "cached_at": datetime.now().isoformat(),
                "cached_ms": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, ttl, json.dumps(payload))
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache account balance: {exc}")
            return False

    async def get_cached_account_balance(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:account_balance:cache"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get cached account balance: {exc}")
            return None


__all__ = ["AccountBalanceCacheMixin"]
