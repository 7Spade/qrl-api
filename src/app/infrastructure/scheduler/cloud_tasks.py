"""
Scheduler shim exposing the consolidated Cloud Tasks router.
"""

from src.app.interfaces.tasks.router import router

__all__ = ["router"]
