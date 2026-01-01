"""
Centralized router registry for QRL Trading API.

This module provides a single point of router registration,
eliminating the need to modify main.py when adding new routes.

Phase 1 Implementation:
- Consolidates all HTTP and Task router imports
- Provides centralized registration function
- Maintains graceful error handling for optional routers
"""

import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)


def register_all_routers(app: FastAPI) -> None:
    """
    Register all API routers to the FastAPI application.

    This function consolidates router registration from:
    - HTTP endpoints (status, market, account, bot, sub_account)
    - Task endpoints (via tasks aggregator)

    Args:
        app: The FastAPI application instance

    Raises:
        Exception: Critical errors during router registration
    """

    # ===== HTTP Routers =====
    _register_http_routers(app)

    # ===== Task Routers =====
    _register_task_routers(app)

    logger.info("All routers registered successfully via centralized registry")


def _register_http_routers(app: FastAPI) -> None:
    """
    Register all HTTP endpoint routers.

    HTTP routers include:
    - status: /, /dashboard, /health, /status
    - market: /market/*
    - account: /account/*
    - bot: /bot/*
    - sub_account: /account/sub-account/*

    Args:
        app: The FastAPI application instance
    """
    try:
        from src.app.interfaces.http.status import router as status_router
        from src.app.interfaces.http.market import router as market_router
        from src.app.interfaces.http.account import router as account_router
        from src.app.interfaces.http.bot import router as bot_router
        from src.app.interfaces.http.sub_account import router as sub_account_router

        # Register HTTP routers in order
        app.include_router(status_router)
        app.include_router(market_router)
        app.include_router(account_router)
        app.include_router(bot_router)
        app.include_router(sub_account_router)

        logger.info(
            "HTTP routers registered: status, market, account, bot, sub_account"
        )

    except Exception as e:
        logger.error(f"Failed to register HTTP routers: {e}", exc_info=True)
        raise


def _register_task_routers(app: FastAPI) -> None:
    """
    Register all Cloud Task endpoint routers.

    Task routers are aggregated in tasks/router.py and include:
    - /tasks/15-min-job: Primary scheduled task
    - /tasks/rebalance/*: Manual rebalance endpoints
    - /tasks/sync-*: MEXC data sync tasks

    Args:
        app: The FastAPI application instance
    """
    try:
        from src.app.interfaces.tasks.router import router as cloud_tasks_router

        # Register task router aggregator
        app.include_router(cloud_tasks_router)

        logger.info("Task routers registered via tasks aggregator")

    except Exception as e:
        logger.error(f"Failed to register task routers: {e}", exc_info=True)
        raise


__all__ = ["register_all_routers"]
