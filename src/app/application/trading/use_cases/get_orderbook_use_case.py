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
        
        # Parse bid/ask arrays into structured format
        # MEXC returns: [[price, quantity], ...]
        bids = [
            {"price": float(bid[0]), "quantity": float(bid[1]), "total": float(bid[0]) * float(bid[1])}
            for bid in depth_data.get("bids", [])
        ]
        asks = [
            {"price": float(ask[0]), "quantity": float(ask[1]), "total": float(ask[0]) * float(ask[1])}
            for ask in depth_data.get("asks", [])
        ]
        
        return {
            "success": True,
            "source": "api",
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now().isoformat(),
        }
