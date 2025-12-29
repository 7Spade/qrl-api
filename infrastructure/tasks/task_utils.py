import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Optional

logger = logging.getLogger(__name__)


def build_metadata(
    task: str,
    source: Optional[str] = None,
    price_source: Optional[str] = None,
    request_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = {
        "task": task,
        "timestamp": datetime.now().isoformat(),
    }
    if request_id:
        metadata["request_id"] = request_id
    if source:
        metadata["source"] = source
    if price_source:
        metadata["price_source"] = price_source
    if extra:
        metadata.update(extra)
    return metadata


async def run_with_retry(
    op: Callable[[], Awaitable[Any]], retries: int, timeout: float, backoff: float
) -> Any:
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            return await asyncio.wait_for(op(), timeout=timeout)
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
            if attempt == retries:
                raise
            await asyncio.sleep(backoff * (2**attempt))
    raise last_error or RuntimeError("operation failed")


async def safe_set(redis_client: Any, key: str, payload: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    client = getattr(redis_client, "client", None)
    if not client:
        return False
    try:
        data = json.dumps(payload)
        if ttl:
            await client.setex(key, ttl, data)
        else:
            await client.set(key, data)
        return True
    except Exception as exc:  # pragma: no cover - best effort
        logger.debug(f"skip cache set {key}: {exc}")
        return False


async def safe_get(redis_client: Any, key: str) -> Optional[Dict[str, Any]]:
    client = getattr(redis_client, "client", None)
    if not client:
        return None
    try:
        data = await client.get(key)
        return json.loads(data) if data else None
    except Exception as exc:  # pragma: no cover - best effort
        logger.debug(f"skip cache get {key}: {exc}")
        return None


class TaskMetrics:
    def __init__(self, redis_client: Any):
        self.redis = redis_client

    async def incr(self, name: str) -> None:
        client = getattr(self.redis, "client", None)
        if not client:
            logger.info(f"[metric] {name}+1 (no redis)")
            return
        try:
            await client.incr(f"metrics:{name}")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug(f"metric {name} skipped: {exc}")

    async def set_value(self, name: str, value: Any, ttl: int = 3600) -> None:
        client = getattr(self.redis, "client", None)
        if not client:
            logger.info(f"[metric] {name}={value} (no redis)")
            return
        try:
            await client.set(f"metrics:{name}", str(value), ex=ttl)
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug(f"metric set {name} skipped: {exc}")
