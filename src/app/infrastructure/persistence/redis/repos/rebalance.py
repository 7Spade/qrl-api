"""Rebalance plan repository mixin."""
from datetime import datetime
import json
from typing import Any, Dict, Optional

from src.app.infrastructure.config import config


class RebalanceRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_rebalance_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Store the latest rebalance plan and append to history.
        """
        client = self._redis_client
        if not client:
            return False

        try:
            key = f"bot:{config.TRADING_SYMBOL}:rebalance:last"
            history_key = f"bot:{config.TRADING_SYMBOL}:rebalance:history"

            enriched = plan.copy()
            enriched.setdefault("timestamp", datetime.now().isoformat())

            payload = json.dumps(enriched)
            await client.set(key, payload)
            await client.lpush(history_key, payload)
            await client.ltrim(history_key, 0, 49)
            await client.expire(history_key, 86400 * 30)
            return True
        except Exception:
            return False

    async def get_rebalance_plan(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the last stored rebalance plan.
        """
        client = self._redis_client
        if not client:
            return None

        try:
            key = f"bot:{config.TRADING_SYMBOL}:rebalance:last"
            payload = await client.get(key)
            return json.loads(payload) if payload else None
        except Exception:
            return None


__all__ = ["RebalanceRepoMixin"]
