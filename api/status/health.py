"""Health check route."""
from datetime import datetime
import logging
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    redis_url_configured: bool
    mexc_api_configured: bool
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    from infrastructure.config import config
    from infrastructure.external.redis_client import redis_client

    mexc_api_configured = bool(config.MEXC_API_KEY and config.MEXC_SECRET_KEY)
    redis_url_configured = bool(config.REDIS_URL or config.REDIS_HOST)
    try:
        if not redis_client.connected:
            await redis_client.connect()
        redis_connected = await redis_client.health_check()
    except Exception as exc:  # pragma: no cover - best effort signal
        logger.error("Redis health check failed", exc_info=True)
        redis_connected = False

    status = "healthy" if mexc_api_configured and redis_connected else "degraded"
    logger.info(
        "Health check",
        extra={
            "status": status,
            "mexc_api_configured": mexc_api_configured,
            "redis_connected": redis_connected,
            "redis_url_configured": redis_url_configured,
        },
    )
    return HealthResponse(
        status=status,
        redis_connected=redis_connected,
        redis_url_configured=redis_url_configured,
        mexc_api_configured=mexc_api_configured,
        timestamp=datetime.now().isoformat(),
    )
