"""
Account trade history use case - get user's executed trades.
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_trades(symbol: str, mexc_client, limit: int = 50) -> Dict[str, Any]:
    """
    Get user's trade history for a symbol from MEXC API.
    
    Args:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        mexc_client: MEXC API client instance with credentials
        limit: Maximum number of trades to return (default: 50)
        
    Returns:
        Dict with trades data including count and timestamp
        
    Raises:
        Exception: If API call fails
    """
    logger.info(f"Fetching trade history for {symbol} from MEXC API (limit={limit})")
    
    try:
        async with mexc_client:
            trades = await mexc_client.get_my_trades(symbol, limit=limit)
            logger.info(f"Retrieved {len(trades)} trades for {symbol}")
            
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "trades": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get trades for {symbol}: {e}")
        return {
            "success": False,
            "symbol": symbol,
            "trades": [],
            "error": str(e),
        }
