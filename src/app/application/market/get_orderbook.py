"""
Market orderbook use case - get order book depth for a symbol.
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_orderbook(symbol: str, mexc_client, limit: int = 20) -> Dict[str, Any]:
    """
    Get order book depth for a symbol from MEXC API.
    
    Args:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        mexc_client: MEXC API client instance
        limit: Number of bids/asks to return (default: 20)
        
    Returns:
        Dict with orderbook data including bids, asks, and timestamp
        
    Raises:
        Exception: If API call fails
    """
    logger.info(f"Fetching orderbook for {symbol} from MEXC API (limit={limit})")
    
    async with mexc_client:
        depth_data = await mexc_client.get_orderbook(symbol, limit=limit)
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "bids": depth_data.get("bids", []),
            "asks": depth_data.get("asks", []),
            "timestamp": datetime.now().isoformat(),
        }
