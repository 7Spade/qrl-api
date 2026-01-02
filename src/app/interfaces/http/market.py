"""
Market HTTP routes - provides endpoints for market data.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Optional

from src.app.application.trading.use_cases.get_price_use_case import get_price
from src.app.application.trading.use_cases.get_orderbook_use_case import get_orderbook
from src.app.application.trading.use_cases.get_klines_use_case import get_klines

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


def _get_mexc_client():
    """Get MEXC client instance from infrastructure."""
    from src.app.infrastructure.external import mexc_client
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


@router.get("/ticker/{symbol}")
async def ticker_endpoint(symbol: str):
    """Get 24-hour ticker data for a symbol."""
    mexc_client = _get_mexc_client()
    try:
        logger.info(f"Fetching ticker for {symbol} from MEXC API")
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": ticker,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exchange-info")
async def exchange_info_endpoint(symbol: Optional[str] = None):
    """Get exchange info / symbol trading rules."""
    mexc_client = _get_mexc_client()
    try:
        async with mexc_client:
            info = await mexc_client.get_exchange_info(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": info,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get exchange info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/book-ticker/{symbol}")
async def book_ticker_endpoint(symbol: str):
    """Best bid/ask for a symbol."""
    mexc_client = _get_mexc_client()
    try:
        async with mexc_client:
            book = await mexc_client.get_book_ticker(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": book,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get book ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{symbol}")
async def trades_endpoint(symbol: str, limit: int = 200):
    """Get recent trades for a symbol."""
    mexc_client = _get_mexc_client()
    try:
        logger.info(f"Fetching recent trades for {symbol} from MEXC API")
        async with mexc_client:
            trades = await mexc_client.get_recent_trades(symbol, limit)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get recent trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agg-trades/{symbol}")
async def agg_trades_endpoint(
    symbol: str,
    limit: int = 200,
    from_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    """Get compressed aggregate trades list."""
    mexc_client = _get_mexc_client()
    try:
        async with mexc_client:
            trades = await mexc_client.get_aggregate_trades(
                symbol=symbol,
                limit=limit,
                from_id=from_id,
                start_time=start_time,
                end_time=end_time,
            )
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get aggregate trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
