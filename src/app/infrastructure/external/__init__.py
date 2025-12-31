"""
External integrations module - re-exports from legacy infrastructure.

This adapter allows src/app code to import external clients without
depending on root-level infrastructure directly.
"""
from infrastructure.external.mexc_client import mexc_client, MEXCClient
from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL
from infrastructure.external.redis_client import redis_client

__all__ = ["mexc_client", "MEXCClient", "redis_client", "QRL_USDT_SYMBOL"]
