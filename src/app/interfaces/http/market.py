"""
HTTP controller shim for market routes.

Re-exports the existing legacy router to keep behavior unchanged.
"""

from api.market_routes import router as legacy_router

router = legacy_router

__all__ = ["router"]
