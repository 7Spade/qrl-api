"""
Helpers for Cloud Tasks: redis wrapper, serialization and retry helper.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Callable

import orjson

logger = logging.getLogger(__name__)

# Best-effort Redis import
try:
    from infrastructure.external.redis_client.client import redis_client
except Exception:
    redis_client = None

# TTLs
BALANCE_TTL = 90
PRICE_TTL = 300
LAST_PRICE_TTL = 24 * 60 * 60


def _serialize(obj: Any) -> str:
    b = orjson.dumps(obj)
    try:
        return b.decode()
    except Exception:
        return b


async def _with_retries(fn: Callable[[], Any], attempts: int = 3, base_backoff: float = 0.5):
    """Simple exponential backoff wrapper for an async callable.

    fn: zero-argument coroutine function.
    """
    last_exc = None
    for i in range(attempts):
        try:
            return await fn()
        except Exception as e:
            last_exc = e
            delay = base_backoff * (2 ** i)
            logger.warning("Transient error, retrying in %.2fs: %s", delay, e)
            await asyncio.sleep(delay)
    raise last_exc


async def safe_redis_set(key: str, value: Any, ttl: int | None = None) -> None:
    if not redis_client:
        return
    try:
        await redis_client.set(key, _serialize(value))
        if ttl:
            try:
                await redis_client.expire(key, ttl)
            except Exception:
                # some wrappers may not expose expire; ignore
                pass
    except Exception as e:
        logger.warning("Failed to write to Redis key %s: %s", key, e)


async def safe_redis_get(key: str):
    if not redis_client:
        return None
    try:
        raw = await redis_client.get(key)
        if not raw:
            return None
        if isinstance(raw, (bytes, str)):
            return orjson.loads(raw)
        # if wrapper returns python object, pass it through
        return raw
    except Exception as e:
        logger.warning("Failed to read Redis key %s: %s", key, e)
        return None
