"""
Redis connection shim exposing the legacy RedisClient singleton.
"""

from src.app.infrastructure.persistence.redis import RedisClient, redis_client

__all__ = ["RedisClient", "redis_client"]
