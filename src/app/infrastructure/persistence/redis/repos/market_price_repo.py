"""
Redis market price repository shim.

Re-exports the legacy MarketCacheMixin to keep cache behavior unchanged.
"""

from src.app.infrastructure.persistence.redis.market_cache import MarketCacheMixin

__all__ = ["MarketCacheMixin"]
