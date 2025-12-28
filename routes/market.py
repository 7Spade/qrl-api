"""
Market Data Routes
"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from config import config
from mexc_client import mexc_client
from redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get market ticker for a symbol"""
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_ticker = await redis_client.get_ticker_24hr(symbol)
            if cached_ticker:
                logger.debug(f"Retrieved ticker from cache for {symbol}")
                return {
                    "symbol": symbol,
                    "data": cached_ticker,
                    "timestamp": cached_ticker.get("cached_at"),
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        ticker = await mexc_client.get_ticker_24hr(symbol)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_ticker_24hr(symbol, ticker)
        
        return {
            "symbol": symbol,
            "data": ticker,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker: {str(e)}")


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price_data = await mexc_client.get_ticker_price(symbol)
        
        # Cache in Redis if connected
        if redis_client.connected and symbol == config.TRADING_SYMBOL:
            price = float(price_data.get("price", 0))
            await redis_client.set_latest_price(price)
            await redis_client.add_price_to_history(price)
        
        return {
            "symbol": symbol,
            "price": price_data.get("price"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 100):
    """
    Get order book depth for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        limit: Depth limit (default 100, max 5000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_orderbook = await redis_client.get_order_book(symbol)
            if cached_orderbook:
                logger.debug(f"Retrieved order book from cache for {symbol}")
                return {
                    "symbol": symbol,
                    "data": cached_orderbook,
                    "timestamp": cached_orderbook.get("cached_at"),
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        orderbook = await mexc_client.get_order_book(symbol, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_order_book(symbol, orderbook)
        
        return {
            "symbol": symbol,
            "data": orderbook,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get order book: {str(e)}")


@router.get("/trades/{symbol}")
async def get_recent_trades(symbol: str, limit: int = 500):
    """
    Get recent trades for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        limit: Number of trades (default 500, max 1000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_trades = await redis_client.get_recent_trades(symbol)
            if cached_trades:
                logger.debug(f"Retrieved recent trades from cache for {symbol}")
                return {
                    "symbol": symbol,
                    "trades": cached_trades,
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        trades = await mexc_client.get_recent_trades(symbol, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_recent_trades(symbol, trades)
        
        return {
            "symbol": symbol,
            "trades": trades,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get recent trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent trades: {str(e)}")


@router.get("/klines/{symbol}")
async def get_klines(symbol: str, interval: str = "1m", limit: int = 500):
    """
    Get klines/candlestick data for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        interval: Kline interval (e.g., "1m", "5m", "15m", "1h", "1d")
        limit: Number of klines (default 500, max 1000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_klines = await redis_client.get_klines(symbol, interval)
            if cached_klines:
                logger.debug(f"Retrieved klines from cache for {symbol} ({interval})")
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "klines": cached_klines,
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        klines = await mexc_client.get_klines(symbol, interval, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_klines(symbol, interval, klines)
        
        return {
            "symbol": symbol,
            "interval": interval,
            "klines": klines,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get klines: {str(e)}")
