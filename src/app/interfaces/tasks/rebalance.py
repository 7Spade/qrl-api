"""
Cloud Scheduler entrypoint for symmetric (equal-value) rebalance planning.
"""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.app.application.account.sync_balance import _require_scheduler_auth
from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/rebalance/symmetric")
async def task_rebalance_symmetric(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    auth_method = _require_scheduler_auth(x_cloudscheduler, authorization)

    try:
        if not redis_client.connected:
            await redis_client.connect()

        balance_service = BalanceService(mexc_client, redis_client)
        rebalance_service = RebalanceService(balance_service, redis_client)
        plan = await rebalance_service.generate_plan()

        return {
            "status": "success",
            "task": "rebalance-symmetric",
            "auth": auth_method,
            "plan": plan,
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - network path
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "task_rebalance_50_50"]
