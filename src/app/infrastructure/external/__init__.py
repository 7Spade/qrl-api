"""
External integrations module - re-exports from legacy infrastructure.

This adapter allows src/app code to import external clients without
depending on root-level infrastructure directly.
"""
from infrastructure.external.mexc_client import mexc_client, MEXCClient
from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL
from src.app.infrastructure.persistence.redis import redis_client, RedisClient

__all__ = ["mexc_client", "MEXCClient", "redis_client", "RedisClient", "QRL_USDT_SYMBOL"]
