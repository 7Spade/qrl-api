"""
Cloud Task handler for syncing market price (application layer).
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import Header, HTTPException, params

from src.app.infrastructure.external import mexc_client

logger = logging.getLogger(__name__)


def _require_scheduler_auth(
    x_cloudscheduler: Optional[str], authorization: Optional[str]
) -> str:
    if isinstance(x_cloudscheduler, params.Header):
        x_cloudscheduler = None
    if isinstance(authorization, params.Header):
        authorization = None
    if not x_cloudscheduler and not authorization:
        raise HTTPException(
            status_code=401, detail="Unauthorized - Cloud Scheduler only"
        )
    return "OIDC" if authorization else "X-CloudScheduler"


async def task_update_price(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
) -> dict[str, object]:
    auth_method = _require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[Cloud Task] 05-min-job authenticated via {auth_method}")

    try:
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            price_change_pct = float(ticker.get("priceChangePercent", 0))
            high_24h = float(ticker.get("highPrice", 0))
            low_24h = float(ticker.get("lowPrice", 0))

        logger.info(
            "[Cloud Task] Price fetched (Direct API) - "
            f"Price: {price:.5f}, Change: {price_change_pct:.2f}%, "
            f"Volume: {volume_24h:.2f}"
        )

        return {
            "status": "success",
            "task": "05-min-job",
            "data": {
                "price": price,
                "volume_24h": volume_24h,
                "price_change_percent": price_change_pct,
                "high_24h": high_24h,
                "low_24h": low_24h,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:  # pragma: no cover - network call
        logger.error(f"[Cloud Task] Price update failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["task_update_price"]
