"""
HTTP controller shim for status routes.

Re-exports the existing legacy router to maintain current behavior.
"""

from api.status_routes import router as legacy_router

router = legacy_router

__all__ = ["router"]
