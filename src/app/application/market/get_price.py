"""
Market price use case - get current price for a symbol from MEXC.
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_price(symbol: str, mexc_client) -> Dict[str, Any]:
    """
    Get current price for a symbol from MEXC API.
    
    Args:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        mexc_client: MEXC API client instance
        
    Returns:
        Dict with price data including symbol, price, and timestamp
        
    Raises:
        Exception: If API call fails
    """
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
