import logging
from typing import Any, Dict, Optional, Tuple

from infrastructure.config.config import config
from infrastructure.external.mexc_client.account import build_balance_map
from infrastructure.tasks.task_utils import safe_get, safe_set

logger = logging.getLogger(__name__)


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class TaskMarketRepo:
    def __init__(self, redis_client: Any):
        self.redis = redis_client

    async def fetch_ticker(self, mexc: Any, symbol: str) -> Dict[str, Any]:
        ticker = await mexc.get_ticker_24hr(symbol)
        price = _safe_float(ticker.get("lastPrice")) or _safe_float(ticker.get("price"))
        return {
            "price": price,
            "volume": _safe_float(ticker.get("volume")),
            "price_change_percent": _safe_float(ticker.get("priceChangePercent")),
            "high": _safe_float(ticker.get("highPrice")),
            "low": _safe_float(ticker.get("lowPrice")),
            "raw": ticker,
        }

    async def fetch_price(self, mexc: Any, symbol: str) -> Tuple[Optional[float], str]:
        ticker = await mexc.get_ticker_price(symbol)
        price = _safe_float(ticker.get("price"))
        if price is not None:
            return price, "exchange"
        cached_price, src = await self.get_cached_price(symbol)
        return cached_price, src or "missing"

    async def get_cached_price(self, symbol: str) -> Tuple[Optional[float], Optional[str]]:
        for key, src in [
            (f"mexc:price:{symbol}", "cache"),
            (f"mexc:price:last:{symbol}", "cache-last"),
            ("mexc:qrl_price", "legacy" if symbol == config.TRADING_SYMBOL else None),
        ]:
            if not src:
                continue
            cached = await safe_get(self.redis, key)
            price = _safe_float(cached.get("price")) if cached else None
            if price is not None:
                return price, src
        return None, None

    async def cache_price(self, symbol: str, payload: Dict[str, Any], ttl_main: int = 300) -> None:
        await safe_set(self.redis, f"mexc:price:{symbol}", payload, ttl_main)
        await safe_set(self.redis, f"mexc:price:last:{symbol}", payload, 86400)


class TaskAccountRepo:
    def __init__(self, market_repo: TaskMarketRepo):
        self.market = market_repo

    async def balance_snapshot(self, mexc: Any) -> Dict[str, Any]:
        account_info = await mexc.get_account_info()
        balances = build_balance_map(account_info)
        price, price_source = await self.market.fetch_price(mexc, config.TRADING_SYMBOL)
        balances.setdefault("QRL", {"free": "0", "locked": "0", "total": 0})
        balances.setdefault("USDT", {"free": "0", "locked": "0", "total": 0})
        snapshot = {
            "balances": balances,
            "prices": {},
            "raw": {"account": account_info},
            "metadata": {
                "price_source": price_source,
                "price_missing": price is None,
            },
        }
        if price is not None:
            snapshot["prices"][config.TRADING_SYMBOL] = price
            snapshot["balances"]["QRL"]["price"] = price
        return snapshot
