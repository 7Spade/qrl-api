"""
Market HTTP routes - provides endpoints for market data.
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Optional

from src.app.application.market.get_price import get_price
from src.app.application.market.get_orderbook import get_orderbook
from src.app.application.market.get_klines import get_klines

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


def _get_mexc_client():
    """Get MEXC client instance from infrastructure."""
    from infrastructure.external import mexc_client
    return mexc_client


@router.get("/price/{symbol}")
async def price_endpoint(symbol: str):
    """Get current price for a symbol (Direct MEXC API)."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_price(symbol, mexc_client)
        return result
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{symbol}")
async def orderbook_endpoint(symbol: str, limit: int = 20):
    """Get order book depth for a symbol."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_orderbook(symbol, mexc_client, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to get orderbook for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/klines/{symbol}")
async def klines_endpoint(
    symbol: str,
    interval: str = "1m",
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    """Get candlestick (kline) data."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_klines(
            symbol=symbol,
            mexc_client=mexc_client,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy routes still mounted for compatibility
from api.market.ticker import router as ticker_router
from api.market.exchange_info import router as exchange_info_router
from api.market.book_ticker import router as book_ticker_router
from api.market.trades import router as trades_router
from api.market.agg_trades import router as agg_trades_router

# Include legacy routers for endpoints not yet migrated
router.include_router(ticker_router)
router.include_router(exchange_info_router)
router.include_router(book_ticker_router)
router.include_router(trades_router)
router.include_router(agg_trades_router)

__all__ = ["router"]
