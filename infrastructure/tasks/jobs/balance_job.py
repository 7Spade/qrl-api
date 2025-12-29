import logging
import uuid
from typing import Any, Dict, Optional

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client
from infrastructure.tasks.task_repos import TaskAccountRepo, TaskMarketRepo
from infrastructure.tasks.task_utils import TaskMetrics, build_metadata, run_with_retry, safe_get, safe_set

logger = logging.getLogger(__name__)
SNAPSHOT_TTL = 90


def _request_id(value: Optional[str]) -> str:
    return value or str(uuid.uuid4())


async def _ensure_redis() -> Any:
    if not redis_client.connected:
        await redis_client.connect()
    return redis_client


async def run_balance_job(request_id: Optional[str] = None, redis_override: Any = None, mexc_override: Any = None) -> Dict[str, Any]:
    request_id = _request_id(request_id)
    redis_inst = redis_override or await _ensure_redis()
    metrics = TaskMetrics(redis_inst)
    market_repo = TaskMarketRepo(redis_inst)
    account_repo = TaskAccountRepo(market_repo)
    client = mexc_override or mexc_client

    async def fetch() -> Dict[str, Any]:
        async with client:
            return await account_repo.balance_snapshot(client)

    try:
        snapshot = await run_with_retry(fetch, retries=1, timeout=10, backoff=1)
        meta = build_metadata(
            task="01-min-job",
            source="exchange",
            price_source=snapshot.get("metadata", {}).get("price_source"),
            request_id=request_id,
            extra={"price_missing": snapshot.get("metadata", {}).get("price_missing", False)},
        )
        snapshot.setdefault("metadata", {}).update(meta)
        await safe_set(redis_inst, "mexc:balance:snapshot", snapshot, SNAPSHOT_TTL)
        await safe_set(redis_inst, "mexc:balance:last", snapshot)
        await metrics.incr("balance_sync_success")
        status = "partial" if snapshot["metadata"].get("price_missing") else "success"
        logger.info(
            "[01-min-job] balance synced",
            extra={"request_id": request_id, "price_source": meta.get("price_source")},
        )
        return {"status": status, "data": snapshot}
    except Exception as exc:  # pragma: no cover - defensive
        await metrics.incr("balance_sync_fail")
        fallback = await safe_get(redis_inst, "mexc:balance:last")
        meta = build_metadata("01-min-job", source="fallback", request_id=request_id, extra={"error": str(exc)})
        logger.error(
            "[01-min-job] balance failed",
            extra={"request_id": request_id, "error": str(exc)},
        )
        if fallback:
            fallback.setdefault("metadata", {}).update(meta)
            return {"status": "degraded", "data": fallback}
        return {"status": "error", "error": str(exc), "metadata": meta}
