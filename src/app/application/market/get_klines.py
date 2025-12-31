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
    
    async with mexc_client:
        klines = await mexc_client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "interval": interval,
            "data": klines,
            "count": len(klines),
            "timestamp": datetime.now().isoformat(),
        }
