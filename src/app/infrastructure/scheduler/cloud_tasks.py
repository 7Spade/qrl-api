"""
Scheduler shim exposing the legacy cloud tasks router.
"""

from infrastructure.tasks.router import router

__all__ = ["router"]
