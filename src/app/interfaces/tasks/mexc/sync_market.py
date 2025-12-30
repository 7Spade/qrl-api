"""
Cloud task entrypoint for market price sync.

Delegates to the legacy handler to preserve existing behavior.
"""

from fastapi import APIRouter

from infrastructure.tasks.mexc_tasks_core import task_update_price

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])
router.add_api_route("/05-min-job", task_update_price, methods=["POST"])

__all__ = ["router"]
