"""
External integrations module - re-exports from native implementations.

This adapter provides access to external clients from a stable import path.
"""
from src.app.infrastructure.external.mexc import mexc_client, MEXCClient
from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL
from src.app.infrastructure.persistence.redis import redis_client, RedisClient

__all__ = ["mexc_client", "MEXCClient", "redis_client", "RedisClient", "QRL_USDT_SYMBOL"]
