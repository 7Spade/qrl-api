from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from infrastructure.external.mexc_client import mexc_client
from .task_helpers import _with_retries, safe_redis_get, safe_redis_set, PRICE_TTL, LAST_PRICE_TTL
from . import metrics
import orjson

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/05-min-job")
async def task_update_price(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")

    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 05-min-job authenticated via {auth_method}")

    async def _fetch_ticker():
        async with mexc_client:
            return await mexc_client.get_ticker_24hr("QRLUSDT")

    ticker = None
    try:
        ticker = await _with_retries(_fetch_ticker, attempts=2)
    except Exception as e:
        logger.warning(f"[Cloud Task] Exchange ticker fetch failed: {e}")

    price = None
    volume_24h = 0.0
    price_change_pct = 0.0
    high_24h = 0.0
    low_24h = 0.0
    metadata = {"source": "exchange", "task": "05-min-job"}

    if isinstance(ticker, dict):
        last_raw = ticker.get("lastPrice")
        try:
            price = float(last_raw) if last_raw is not None else None
        except Exception:
            price = None
        try:
            volume_24h = float(ticker.get("volume") or 0)
            price_change_pct = float(ticker.get("priceChangePercent") or 0)
            high_24h = float(ticker.get("highPrice") or 0)
            low_24h = float(ticker.get("lowPrice") or 0)
        except Exception:
            pass

    if price is None:
        last = await safe_redis_get("mexc:price:last:QRLUSDT")
        if last and isinstance(last, dict):
            try:
                price = float(last.get("price"))
                metadata["price_source"] = "redis_fallback"
                metrics.price_missing_count.inc()
            except Exception:
                metadata["price_missing"] = True
                metrics.price_missing_count.inc()
        else:
            metadata["price_missing"] = True
            metrics.price_missing_count.inc()

    payload = {"price": price, "volume_24h": volume_24h, "price_change_percent": price_change_pct, "high_24h": high_24h, "low_24h": low_24h, "metadata": metadata, "timestamp": datetime.utcnow().isoformat() + "Z"}

    # persist best-effort
    await safe_redis_set("mexc:price:QRLUSDT", payload, ttl=PRICE_TTL)
    await safe_redis_set("mexc:price:last:QRLUSDT", {"price": price, "timestamp": payload["timestamp"]}, ttl=LAST_PRICE_TTL)

    if price is not None:
        metrics.price_fetch_success.inc()
        try:
            metrics.last_price_gauge.set(price)
        except Exception:
            pass
    else:
        metrics.price_fetch_failure.inc()

    logger.info(f"[Cloud Task] Price update - Price: {price if price is not None else 'N/A'}")
    return {"status": "success", "task": "05-min-job", "data": payload}
