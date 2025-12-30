"""
HTTP controller shim for bot routes.

Re-exports the existing legacy router to preserve behavior during migration.
"""

from api.bot_routes import router as legacy_router

router = legacy_router

__all__ = ["router"]
