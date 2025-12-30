"""
Aggregate market cache mixin kept for backward compatibility.
"""
from .market_price_cache import MarketPriceCacheMixin
from .market_trades_cache import MarketTradesCacheMixin


class MarketCacheMixin(MarketPriceCacheMixin, MarketTradesCacheMixin):
    """Backwards-compatible aggregate mixin."""


__all__ = ["MarketCacheMixin", "MarketPriceCacheMixin", "MarketTradesCacheMixin"]
