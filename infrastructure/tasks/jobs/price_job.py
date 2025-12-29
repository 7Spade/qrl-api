import logging
import time
import uuid
from typing import Any, Dict, Optional

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client
from infrastructure.tasks.task_repos import TaskMarketRepo
from infrastructure.tasks.task_utils import TaskMetrics, build_metadata, run_with_retry, safe_get

logger = logging.getLogger(__name__)
PRICE_TTL = 300


def _request_id(value: Optional[str]) -> str:
    return value or str(uuid.uuid4())


async def _ensure_redis() -> Any:
    if not redis_client.connected:
        await redis_client.connect()
    return redis_client


async def run_price_job(request_id: Optional[str] = None, redis_override: Any = None, mexc_override: Any = None) -> Dict[str, Any]:
    request_id = _request_id(request_id)
    redis_inst = redis_override or await _ensure_redis()
    metrics = TaskMetrics(redis_inst)
    market_repo = TaskMarketRepo(redis_inst)
    client = mexc_override or mexc_client

    async def fetch():
        async with client:
            ticker = await market_repo.fetch_ticker(client, config.TRADING_SYMBOL)
            price, price_source = await market_repo.fetch_price(client, config.TRADING_SYMBOL)
            return ticker, price, price_source

    try:
        started = time.monotonic()
        ticker, price, price_source = await run_with_retry(fetch, retries=2, timeout=6, backoff=1)
        latency_ms = int((time.monotonic() - started) * 1000)
        await metrics.set_value("price_fetch_latency", latency_ms)
        prev_price, _ = await market_repo.get_cached_price(config.TRADING_SYMBOL)
        payload = {
            "price": price if price is not None else ticker.get("price"),
            "ticker": ticker,
            "price_source": price_source,
        }
        price_missing = payload["price"] is None
        if price_missing:
            await metrics.incr("price_missing_count")
            fallback_price, fallback_source = await market_repo.get_cached_price(config.TRADING_SYMBOL)
            payload["price"] = fallback_price
            payload["price_source"] = fallback_source or price_source
            price_missing = payload["price"] is None
        if payload["price"] is not None and prev_price is not None and payload["price"] != prev_price:
            await metrics.incr("price_change_count")
        await market_repo.cache_price(config.TRADING_SYMBOL, payload, PRICE_TTL)
        meta = build_metadata(
            task="05-min-job",
            source="exchange" if price_source == "exchange" else "cache",
            price_source=payload.get("price_source"),
            request_id=request_id,
            extra={"price_missing": price_missing},
        )
        logger.info("[05-min-job] price updated", extra={"request_id": request_id, "price_source": payload.get("price_source")})
        status = "partial" if price_missing else "success"
        return {"status": status, "data": payload, "metadata": meta}
    except Exception as exc:  # pragma: no cover - defensive
        await metrics.incr("price_sync_fail")
        fallback_price, fallback_source = await market_repo.get_cached_price(config.TRADING_SYMBOL)
        meta = build_metadata(
            task="05-min-job",
            source="fallback",
            price_source=fallback_source,
            request_id=request_id,
            extra={"error": str(exc), "price_missing": fallback_price is None},
        )
        logger.error("[05-min-job] price failed", extra={"request_id": request_id, "error": str(exc)})
        return {
            "status": "degraded" if fallback_price is not None else "error",
            "data": {"price": fallback_price},
            "metadata": meta,
        }
