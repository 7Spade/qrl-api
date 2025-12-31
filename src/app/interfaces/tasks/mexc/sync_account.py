"""
Cloud task entrypoint for account sync.

Wraps the legacy handler to keep behavior unchanged while matching the target
interfaces/tasks layout.
"""

from fastapi import APIRouter

from src.app.application.account.sync_balance import task_sync_balance

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])
router.add_api_route("/01-min-job", task_sync_balance, methods=["POST"])

__all__ = ["router"]
