"""
HTTP controller shim for account routes.

Keeps legacy handlers untouched by re-exporting the existing router from `api.account_routes`.
"""

from api.account_routes import router as legacy_router

router = legacy_router

__all__ = ["router"]
