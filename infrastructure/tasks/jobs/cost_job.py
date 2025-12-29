import logging
import uuid
from typing import Any, Dict, List, Optional

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client
from infrastructure.tasks.task_repos import TaskAccountRepo, TaskMarketRepo
from infrastructure.tasks.task_utils import TaskMetrics, build_metadata, run_with_retry, safe_get, safe_set
from infrastructure.utils.type_safety import safe_float

logger = logging.getLogger(__name__)


def _request_id(value: Optional[str]) -> str:
    return value or str(uuid.uuid4())


async def _ensure_redis() -> Any:
    if not redis_client.connected:
        await redis_client.connect()
    return redis_client


def _compute_values(snapshot: Dict[str, Any], price: Optional[float]) -> Dict[str, float]:
    balances = snapshot.get("balances", {})
    qrl_total = safe_float(balances.get("QRL", {}).get("total", 0))
    usdt_total = safe_float(balances.get("USDT", {}).get("total", 0))
    qrl_value = (qrl_total or 0) * (price or 0)
    return {
        "qrl_total": qrl_total or 0,
        "usdt_total": usdt_total or 0,
        "price": price,
        "total_value_usdt": (usdt_total or 0) + qrl_value,
    }


async def run_cost_job(request_id: Optional[str] = None, redis_override: Any = None, mexc_override: Any = None) -> Dict[str, Any]:
    request_id = _request_id(request_id)
    redis_inst = redis_override or await _ensure_redis()
    metrics = TaskMetrics(redis_inst)
    market_repo = TaskMarketRepo(redis_inst)
    account_repo = TaskAccountRepo(market_repo)
    client = mexc_override or mexc_client
    alerts: List[str] = []

    snapshot = await safe_get(redis_inst, "mexc:balance:snapshot")
    if not snapshot:
        snapshot = await safe_get(redis_inst, "mexc:balance:last")
    if not snapshot:
        try:
            async with client:
                snapshot = await run_with_retry(
                    lambda: account_repo.balance_snapshot(client), retries=0, timeout=30, backoff=1
                )
        except Exception as exc:  # pragma: no cover - defensive
            alert_meta = build_metadata(
                task="15-min-job", source="error", request_id=request_id, extra={"error": str(exc)}
            )
            alerts.append("snapshot-unavailable")
            return {"status": "error", "alerts": alerts, "metadata": alert_meta}

    price = snapshot.get("prices", {}).get(config.TRADING_SYMBOL)
    price_source = snapshot.get("metadata", {}).get("price_source")
    if price is None:
        price, price_source = await market_repo.get_cached_price(config.TRADING_SYMBOL)
        if price is None:
            alerts.append("price-missing")
            await metrics.incr("price_missing_count")
    values = _compute_values(snapshot, price)
    payload = {"snapshot": snapshot, "values": values, "price_source": price_source}
    await safe_set(redis_inst, "mexc:account:costs", payload)

    alert_counter = await safe_get(redis_inst, "metrics:price_missing_count")
    if alert_counter:
        try:
            if int(alert_counter) >= 3:
                alerts.append("price-missing-threshold")
        except Exception:
            pass
    meta = build_metadata(
        task="15-min-job",
        source="cache" if snapshot.get("metadata", {}).get("source") == "cache" else "exchange",
        price_source=price_source,
        request_id=request_id,
        extra={"alerts": alerts, "price_missing": price is None},
    )
    logger.info("[15-min-job] cost recomputed", extra={"request_id": request_id, "alerts": alerts})
    status = "partial" if price is None else "success"
    return {"status": status, "data": payload, "alerts": alerts, "metadata": meta}
