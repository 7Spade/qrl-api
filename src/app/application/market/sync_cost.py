"""
Cloud Task handler for cost/price check (application layer).
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


async def task_update_cost(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
) -> dict[str, object]:
    auth_method = _require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[Cloud Task] 15-min-job authenticated via {auth_method}")

    try:
        async with mexc_client:
            ticker = await mexc_client.get_ticker_price("QRLUSDT")
            current_price = float(ticker.get("price", 0))

        logger.info(
            "[Cloud Task] Price check (Direct API) - "
            f"Current: ${current_price:.5f}"
        )

        return {
            "status": "success",
            "task": "15-min-job",
            "data": {"current_price": current_price},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:  # pragma: no cover - network call
        logger.error(f"[Cloud Task] Cost update failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["task_update_cost"]
