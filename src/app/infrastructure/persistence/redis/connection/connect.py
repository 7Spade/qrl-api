"""
Redis connection shim exposing the legacy RedisClient singleton.
"""

from infrastructure.external.redis_client import RedisClient, redis_client

__all__ = ["RedisClient", "redis_client"]
