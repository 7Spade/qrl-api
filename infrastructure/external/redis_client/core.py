"""Compatibility shim exposing the async Redis client at the legacy path."""
from .asyncio.client import AsyncRedisClient, RedisClient, redis_client

__all__ = ["AsyncRedisClient", "RedisClient", "redis_client"]
