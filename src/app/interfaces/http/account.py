"""
Account HTTP routes aligned to target architecture.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.app.application.account.balance_service import BalanceService

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.external.redis_client import redis_client

    return BalanceService(mexc_client, redis_client)


@router.get("/account/balance", tags=["Account"])
async def get_account_balance():
    """Get account balance with fallback to cached snapshot."""
    try:
        service = _build_balance_service()
        snapshot = await service.get_account_balance()
        BalanceService.to_usd_values(snapshot)
        return snapshot
    except ValueError as exc:
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:  # pragma: no cover - FastAPI will surface HTTP 500
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/account/balance/cache", tags=["Account"])
async def get_cached_balance():
    """Retrieve cached balance without hitting the exchange."""
    from infrastructure.external.redis_client import redis_client

    cached = await redis_client.get_cached_account_balance()
    if cached:
        cached["source"] = "cache"
        cached["timestamp"] = datetime.now().isoformat()
        return cached
    raise HTTPException(status_code=404, detail="No cached balance available")


# Include remaining legacy routers for orders/trades/sub-accounts
from api.account.orders import router as orders_router  # noqa: E402
from api.account.trades import router as trades_router  # noqa: E402
from api.account.sub_accounts import router as sub_accounts_router  # noqa: E402

router.include_router(orders_router)
router.include_router(trades_router)
router.include_router(sub_accounts_router)

__all__ = ["router", "get_account_balance", "get_cached_balance"]
