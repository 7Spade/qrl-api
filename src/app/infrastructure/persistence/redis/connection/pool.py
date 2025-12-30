"""
Redis connection pool shim referencing the shared client instance.
"""

from infrastructure.external.redis_client import RedisClient, redis_client

__all__ = ["RedisClient", "redis_client"]
