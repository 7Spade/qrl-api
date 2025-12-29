from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from infrastructure.external.mexc_client import mexc_client
from .task_helpers import _with_retries, safe_redis_get, safe_redis_set
from . import metrics
import orjson

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/15-min-job")
async def task_reconcile_and_alert(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")

    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 15-min-job authenticated via {auth_method}")

    snapshot = None
    price_payload = None

    snapshot = await safe_redis_get("mexc:balance:snapshot")
    price_payload = await safe_redis_get("mexc:price:QRLUSDT")

    if not snapshot or not price_payload:
        logger.info("[Cloud Task] Missing cached data; attempting best-effort direct fetch")
        async def _fetch_both():
            async with mexc_client:
                acc = await mexc_client.get_account_info()
                tk = await mexc_client.get_ticker_24hr("QRLUSDT")
                return acc, tk

        try:
            acc, tk = await _with_retries(_fetch_both, attempts=2)
            if not snapshot:
                snapshot = {"accounts_raw": acc, "metadata": {"source": "exchange_direct"}}
            if not price_payload:
                price_payload = {"price": tk.get("lastPrice"), "metadata": {"source": "exchange_direct"}}
        except Exception as e:
            logger.warning(f"[Cloud Task] Direct fetch failed during 15-min job: {e}")

    result = {"reconciled": False, "details": {}, "timestamp": datetime.utcnow().isoformat() + "Z"}
    try:
        if snapshot and price_payload:
            try:
                price = price_payload.get("price")
                price = float(price) if price is not None else None
            except Exception:
                price = None

            total_usd = 0.0
            assets = snapshot.get("assets") or snapshot.get("accounts_raw", {}).get("balances", [])
            if isinstance(assets, dict):
                for asset, vals in assets.items():
                    if asset == "QRL" and price:
                        total_usd += float(vals.get("total", 0)) * price
                    elif asset == "USDT":
                        total_usd += float(vals.get("total", 0))
            elif isinstance(assets, list):
                for b in assets:
                    if b.get("asset") == "QRL" and price:
                        total_usd += float(b.get("free", 0) or 0) * price
                    if b.get("asset") == "USDT":
                        total_usd += float(b.get("free", 0) or 0)

            result["reconciled"] = True
            result["details"]["estimated_total_usd"] = total_usd
        else:
            result["details"]["note"] = "insufficient_data"
    except Exception as e:
        logger.warning(f"[Cloud Task] Reconciliation error: {e}")
    # persist summary best-effort
    await safe_redis_set("mexc:reconcile:last", result)

    # metrics
    if result.get("reconciled"):
        metrics.reconcile_success.inc()
    else:
        # insufficient or missing
        metrics.reconcile_insufficient.inc()

    return {"status": "success", "task": "15-min-job", "data": result}
