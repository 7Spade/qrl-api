"""
Account HTTP routes aligned to target architecture.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.account.list_orders import get_orders
from src.app.application.account.list_trades import get_trades

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.external.redis_client import redis_client
    return BalanceService(mexc_client, redis_client)


def _get_mexc_client():
    from infrastructure.external.mexc_client import mexc_client
    return mexc_client


def _has_credentials(mexc_client) -> bool:
    return bool(
        getattr(mexc_client, "api_key", None)
        and getattr(mexc_client, "secret_key", None)
    )


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
    except Exception as exc:
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


@router.get("/orders")
async def orders_endpoint():
    """Get user's open orders for QRL/USDT (real-time from MEXC API)."""
    mexc_client = _get_mexc_client()
    if not _has_credentials(mexc_client):
        raise HTTPException(
            status_code=503, detail="MEXC API credentials required for orders"
        )
    
    try:
        from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL
        result = await get_orders(QRL_USDT_SYMBOL, mexc_client)
        return result
    except Exception as e:
        logger.error(f"Failed to get orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def trades_endpoint(symbol: str = "QRLUSDT", limit: int = 50):
    """Get user's trade history (real-time from MEXC API)."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_trades(symbol, mexc_client, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to get trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include remaining legacy sub-account router
from api.account.sub_accounts import router as sub_accounts_router

router.include_router(sub_accounts_router)

__all__ = ["router"]
