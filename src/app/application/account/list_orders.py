"""
Account open orders use case - get user's current open orders.
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_orders(symbol: str, mexc_client) -> Dict[str, Any]:
    """
    Get user's open orders for a symbol from MEXC API.
    
    Args:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        mexc_client: MEXC API client instance with credentials
        
    Returns:
        Dict with orders data including count and timestamp
        
    Raises:
        Exception: If API call fails or credentials missing
    """
    logger.info(f"Fetching open orders for {symbol} from MEXC API")
    
    async with mexc_client:
        orders = await mexc_client.get_open_orders(symbol)
        logger.info(f"Retrieved {len(orders)} open orders for {symbol}")
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.now().isoformat(),
        }
