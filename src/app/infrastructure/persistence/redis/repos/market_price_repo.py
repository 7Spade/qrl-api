"""
Redis market price repository shim.

Re-exports the legacy MarketCacheMixin to keep cache behavior unchanged.
"""

from infrastructure.external.redis_client.market_cache import MarketCacheMixin

__all__ = ["MarketCacheMixin"]
