"""
HTTP controller shim for sub-account routes.

Re-exports the existing legacy router to keep current functionality intact.
"""

from api.sub_account_routes import router as legacy_router

router = legacy_router

__all__ = ["router"]
