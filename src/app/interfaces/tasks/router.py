"""
Task interface shim that re-exports the legacy task router.

This keeps current behavior untouched while aligning imports with the
target `interfaces/tasks` layout described in the architecture docs.
"""

from infrastructure.tasks.router import router as legacy_router

router = legacy_router

__all__ = ["router"]
