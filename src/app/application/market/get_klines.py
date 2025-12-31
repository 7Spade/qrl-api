"""
Market klines (candlestick) use case - get historical OHLCV data.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def get_klines(
    symbol: str,
    mexc_client,
    interval: str = "1m",
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get candlestick (kline) data for a symbol from MEXC API.
    
    Args:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        mexc_client: MEXC API client instance
        interval: Kline interval (e.g., "1m", "5m", "1h", "1d")
        limit: Number of klines to return (default: 100)
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        
    Returns:
        Dict with klines data array and metadata
        
    Raises:
        Exception: If API call fails
    """
    logger.info(f"Fetching klines for {symbol} from MEXC API (interval={interval}, limit={limit})")
    
    # Validate symbol format
    if not symbol or not symbol.isupper():
        symbol = symbol.upper()
    
    async with mexc_client:
        klines_raw = await mexc_client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Parse K-line arrays into structured format
        # MEXC returns: [[openTime, open, high, low, close, volume, closeTime, quoteVolume, ...]]
        klines = [
            {
                "open_time": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": int(k[6]),
                "quote_volume": float(k[7]) if len(k) > 7 else 0.0,
            }
            for k in klines_raw
        ]
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "interval": interval,
            "data": klines,
            "count": len(klines),
            "timestamp": datetime.now().isoformat(),
        }
