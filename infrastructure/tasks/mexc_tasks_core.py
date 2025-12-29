"""
Cloud Scheduler Tasks routed through repository/service helpers.
"""
import logging
from fastapi import APIRouter, Header, HTTPException

from infrastructure.tasks.jobs import run_balance_job, run_cost_job, run_price_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


def _require_scheduler(x_cloudscheduler: str | None, authorization: str | None) -> str:
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    return "OIDC" if authorization else "X-CloudScheduler"


@router.post("/01-min-job")
async def task_sync_balance(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None),
    request_id: str | None = Header(None, alias="X-Request-ID"),
):
    auth_method = _require_scheduler(x_cloudscheduler, authorization)
    logger.info("[Cloud Task] 01-min-job authenticated", extra={"auth": auth_method})
    return await run_balance_job(request_id=request_id)


@router.post("/05-min-job")
async def task_update_price(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None),
    request_id: str | None = Header(None, alias="X-Request-ID"),
):
    auth_method = _require_scheduler(x_cloudscheduler, authorization)
    logger.info("[Cloud Task] 05-min-job authenticated", extra={"auth": auth_method})
    return await run_price_job(request_id=request_id)


@router.post("/15-min-job")
async def task_update_cost(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None),
    request_id: str | None = Header(None, alias="X-Request-ID"),
):
    auth_method = _require_scheduler(x_cloudscheduler, authorization)
    logger.info("[Cloud Task] 15-min-job authenticated", extra={"auth": auth_method})
    return await run_cost_job(request_id=request_id)
