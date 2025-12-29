"""
Account balance route with cache-aware balance service.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

from services.account import BalanceService

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.external.redis_client import redis_client

    return BalanceService(mexc_client, redis_client)


@router.get("/balance")
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


@router.get("/balance/cache")
async def get_cached_balance():
    """Retrieve cached balance without hitting the exchange."""
    from infrastructure.external.redis_client import redis_client

    cached = await redis_client.get_cached_account_balance()
    if cached:
        cached["source"] = "cache"
        cached["timestamp"] = datetime.now().isoformat()
        return cached
    raise HTTPException(status_code=404, detail="No cached balance available")


@router.get("/balance/redis")
async def get_balance_redis():
    """Return persisted MEXC balance data stored in Redis."""
    from infrastructure.external.redis_client import redis_client

    raw = await redis_client.get_mexc_raw_response("account_balance")
    balances = await redis_client.get_mexc_account_balance()
    price = await redis_client.get_mexc_qrl_price()
    total_value = await redis_client.get_mexc_total_value()

    if not any([raw, balances, price, total_value]):
        raise HTTPException(status_code=404, detail="No persisted balance data available")

    return {
        "success": True,
        "source": "redis",
        "raw": raw,
        "balances": balances,
        "price": price,
        "total_value": total_value,
        "timestamp": datetime.now().isoformat(),
    }


__all__ = [
    "router",
    "get_account_balance",
    "get_cached_balance",
    "get_balance_redis",
]
