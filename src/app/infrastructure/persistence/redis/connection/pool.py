"""
Redis connection pool shim referencing the shared client instance.
"""

from src.app.infrastructure.persistence.redis import RedisClient, redis_client

__all__ = ["RedisClient", "redis_client"]
