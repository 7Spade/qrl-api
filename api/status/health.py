"""Health check route."""
from datetime import datetime
import logging
import os
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from infrastructure.config import config
from infrastructure.external import mexc_client as shared_mexc_client
from infrastructure.external import redis_client as shared_redis_client

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    env: str
    mexc_api_configured: bool
    mexc_secret_configured: bool
    redis_configured: bool
    redis_connected: bool
    mexc_reachable: bool
    missing: List[str]
    timestamp: str


def _get_mexc_client():
    return shared_mexc_client


def _get_redis_client():
    return shared_redis_client


def _config_status():
    env = getattr(config, "FLASK_ENV", "unknown")
    api_key_present = bool(getattr(config, "MEXC_API_KEY", None))
    secret_present = bool(
        getattr(config, "MEXC_SECRET_KEY", None) or os.getenv("MEXC_SECRET")
    )
    redis_configured = bool(getattr(config, "REDIS_URL", None))
    missing = []
    if not api_key_present:
        missing.append("MEXC_API_KEY")
    if not secret_present:
        missing.append("MEXC_SECRET_KEY")
    if not redis_configured:
        missing.append("REDIS_URL")
    return env, api_key_present, secret_present, redis_configured, missing


async def _check_mexc_ping(mexc_client) -> bool:
    if not mexc_client:
        return False
    try:
        import asyncio

        await asyncio.wait_for(mexc_client.ping(), timeout=5.0)
        return True
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("MEXC API ping failed: %s", exc)
        return False


async def _check_redis_connection(redis_client) -> bool:
    if not redis_client:
        return False
    try:
        if getattr(redis_client, "connected", False):
            return await redis_client.health_check()
        return await redis_client.connect()
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("Redis health check failed: %s", exc)
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check():
    env, api_key_present, secret_present, redis_configured, missing = _config_status()

    redis_connected = False
    if redis_configured:
        redis_connected = await _check_redis_connection(_get_redis_client())

    mexc_reachable = await _check_mexc_ping(_get_mexc_client())

    status = "healthy"
    if not (
        api_key_present
        and secret_present
        and mexc_reachable
        and (not redis_configured or redis_connected)
    ):
        status = "degraded"


    logger.info(
        (
            "Health check status=%s env=%s has_key=%s has_secret=%s "
            "redis_cfg=%s redis_connected=%s mexc_reachable=%s missing=%s"
        ),
        status,
        env,
        api_key_present,
        secret_present,
        redis_configured,
        redis_connected,
        mexc_reachable,
        ",".join(missing) if missing else "none",
    )

    return HealthResponse(
        status=status,
        env=env,
        mexc_api_configured=api_key_present,
        mexc_secret_configured=secret_present,
        redis_configured=redis_configured,
        redis_connected=redis_connected,
        mexc_reachable=mexc_reachable,
        missing=sorted(set(missing)),
        timestamp=datetime.now().isoformat(),
    )
