from datetime import datetime
import logging
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from .task_helpers import _with_retries, safe_redis_set, _serialize, BALANCE_TTL
from . import metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/01-min-job")
async def task_sync_balance(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")

    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 01-min-job authenticated via {auth_method}")

    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        logger.warning("[Cloud Task] API keys not configured, skipping balance sync")
        return {"status": "skipped", "reason": "API keys not configured"}

    async def _fetch_account():
        async with mexc_client:
            return await mexc_client.get_account_info()

    try:
        account_info = await _with_retries(_fetch_account, attempts=2)

        qrl_balance = 0.0
        usdt_balance = 0.0
        all_balances = {}

        for balance in account_info.get("balances", []) or []:
            asset = balance.get("asset")
            try:
                free = float(balance.get("free") or 0)
                locked = float(balance.get("locked") or 0)
            except Exception:
                free = 0.0
                locked = 0.0

            if free > 0 or locked > 0:
                all_balances[asset] = {"free": str(free), "locked": str(locked), "total": str(free + locked)}

            if asset == "QRL":
                qrl_balance = free
            elif asset == "USDT":
                usdt_balance = free

        snapshot = {
            "qrl_balance": qrl_balance,
            "usdt_balance": usdt_balance,
            "assets": all_balances,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {"source": "exchange", "task": "01-min-job"},
        }

        # best-effort Redis write
        await safe_redis_set("mexc:balance:snapshot", snapshot, ttl=BALANCE_TTL)
        await safe_redis_set("mexc:balance:last", {"snapshot": snapshot, "timestamp": snapshot["timestamp"]})

        metrics.balance_sync_success.inc()
        logger.info(f"[Cloud Task] Balance synced - QRL: {qrl_balance:.2f}, USDT: {usdt_balance:.2f}, assets: {len(all_balances)}")
        return {"status": "success", "task": "01-min-job", "data": {"qrl_balance": qrl_balance, "usdt_balance": usdt_balance, "total_assets": len(all_balances)}, "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"[Cloud Task] Balance sync failed: {e}", exc_info=True)
        metrics.balance_sync_failure.inc()
        return {"status": "partial_failure", "task": "01-min-job", "reason": "balance sync failed", "error": str(e)}
