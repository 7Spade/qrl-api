"""
Compatibility shim for MarketService.
Delegates to services.market.market_service to keep imports stable
after restructuring the service package per README layout.
"""
from services.market.market_service import MarketService

__all__ = ["MarketService"]
