"""
Status and health HTTP routes - system status and health checks.
"""
from datetime import datetime
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)

# Initialize templates with error handling
try:
    templates = Jinja2Templates(directory="src/app/interfaces/templates")
    logger.info("Templates initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize templates: {e} - dashboard will not be available")
    templates = None


class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    mexc_api_configured: bool
    timestamp: str


class StatusResponse(BaseModel):
    bot_status: str
    daily_trades: int
    position: Optional[Dict[str, Any]] = None
    position_layers: Optional[Dict[str, Any]] = None
    timestamp: str


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - returns dashboard HTML."""
    if templates is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"message": "Dashboard unavailable - templates not loaded", "status": "degraded"},
            status_code=503
        )
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard endpoint - returns dashboard HTML."""
    if templates is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"message": "Dashboard unavailable - templates not loaded", "status": "degraded"},
            status_code=503
        )
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - returns system health status."""
    from src.app.infrastructure.config import config

    mexc_api_configured = bool(config.MEXC_API_KEY and config.MEXC_SECRET_KEY)
    status = "healthy" if mexc_api_configured else "degraded"
    logger.info(f"Health check: {status} (MEXC: {mexc_api_configured})")
    return HealthResponse(
        status=status,
        redis_connected=False,
        mexc_api_configured=mexc_api_configured,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Status endpoint - returns bot and trading status."""
    logger.info("Status retrieved - Direct API mode (no Redis)")
    return StatusResponse(
        bot_status="running",
        daily_trades=0,
        position=None,
        position_layers=None,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/api/info", response_model=Dict[str, Any])
async def api_info():
    """API info endpoint - returns API metadata."""
    return {
        "name": "QRL Trading API",
        "version": "1.0.0",
        "status": "running",
        "environment": "production",
        "endpoints": {
            "health": "/health",
            "dashboard": "/dashboard",
            "status": "/status",
            "market": "/market/*",
            "account": "/account/*",
            "bot": "/bot/*",
            "tasks": "/tasks/*",
        },
        "timestamp": datetime.now().isoformat(),
    }


__all__ = ["router", "HealthResponse", "StatusResponse"]
