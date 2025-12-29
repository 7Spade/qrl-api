"""
Market data API routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """
    Get 24-hour ticker data for a symbol (Direct MEXC API)
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

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


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """
    Get current price for a symbol (Direct MEXC API)
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Fetching price for {symbol} from MEXC API")
        async with mexc_client:
            price_data = await mexc_client.get_ticker_price(symbol)
            price = float(price_data.get("price", 0))
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "price": str(price),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exchange-info")
async def get_exchange_info(symbol: Optional[str] = None):
    """
    Get exchange info / symbol trading rules
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

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


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 50):
    """
    Get order book (depth) for a symbol (Direct MEXC API)
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Fetching order book for {symbol} from MEXC API")
        async with mexc_client:
            orderbook = await mexc_client.get_order_book(symbol, limit)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": orderbook,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/book-ticker/{symbol}")
async def get_book_ticker(symbol: str):
    """Best bid/ask for a symbol"""
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

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
async def get_recent_trades(symbol: str, limit: int = 200):
    """
    Get recent trades for a symbol (Direct MEXC API)
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

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
async def get_agg_trades(
    symbol: str,
    limit: int = 200,
    from_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    """Get compressed aggregate trades list"""
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

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
        logger.error(f"Failed to get agg trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = "1m",
    limit: int = 200,
):
    """
    Get candlestick/kline data for a symbol
    """
    from infrastructure.external import mexc_client
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Fetching klines for {symbol}:{interval} from MEXC API")
        async with mexc_client:
            klines = await mexc_client.get_klines(symbol, interval, limit)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "interval": interval,
                "data": klines,
                "count": len(klines),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        return {
            "success": False,
            "symbol": symbol,
            "interval": interval,
            "data": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
