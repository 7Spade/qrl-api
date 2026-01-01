"""
Cloud Scheduler entrypoint for intelligent rebalance planning.

Implements the strategy documented in:
- docs/INTELLIGENT_REBALANCE_FORMULAS.md
- docs/INTELLIGENT_REBALANCE_EXECUTION_GUIDE.md

This endpoint enhances the symmetric rebalance with:
- MA (Moving Average) cross signals
- Cost basis validation
- Position tier management
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.intelligent_rebalance_service import (
    IntelligentRebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client
from src.app.interfaces.tasks.shared import (
    ensure_redis_connected,
    require_scheduler_auth,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/rebalance/intelligent")
async def task_rebalance_intelligent(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    """
    Generate intelligent rebalance plan with MA signals and position management.

    This endpoint implements an enhanced rebalancing strategy that includes:
    - MA (Moving Average) cross signal detection (MA_7 vs MA_25)
    - Cost basis validation (buy low, sell high)
    - Position tier management (70% core, 20% swing, 10% active)

    Decision logic:
    - BUY: Golden cross (MA_7 > MA_25) + price <= cost_avg
    - SELL: Death cross (MA_7 < MA_25) + price >= cost_avg * 1.03
    - HOLD: Otherwise or when within threshold

    Authentication:
        Requires Cloud Scheduler authentication via X-CloudScheduler
        header or OIDC Authorization header.

    Returns:
        dict: Intelligent rebalance plan with:
            - action: HOLD/BUY/SELL
            - MA indicators: ma_short, ma_long, signal
            - position_tiers: core, swing, active
            - signal_validation: price vs cost analysis
    """
    # Step 1: Authenticate
    auth_method = require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[rebalance-intelligent] Authenticated via {auth_method}")

    # Step 2: Ensure Redis connection
    await ensure_redis_connected(redis_client)

    try:
        # Step 3: Generate intelligent rebalance plan
        balance_service = BalanceService(mexc_client, redis_client)
        intelligent_service = IntelligentRebalanceService(
            balance_service=balance_service,
            mexc_client=mexc_client,
            redis_client=redis_client,
        )
        plan = await intelligent_service.generate_plan()

        logger.info(
            f"[rebalance-intelligent] Plan generated - "
            f"Action: {plan.get('action')}, "
            f"Quantity: {plan.get('quantity', 0):.4f}, "
            f"MA Signal: {plan.get('ma_indicators', {}).get('signal', 'N/A')}"
        )

        return {
            "status": "success",
            "task": "rebalance-intelligent",
            "auth": auth_method,
            "plan": plan,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"[rebalance-intelligent] Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"[rebalance-intelligent] Execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "task_rebalance_intelligent"]
