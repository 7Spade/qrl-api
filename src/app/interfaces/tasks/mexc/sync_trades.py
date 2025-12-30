"""
Cloud task entrypoint for trade/cost update.

Delegates to the legacy handler to preserve existing behavior.
"""

from fastapi import APIRouter

from infrastructure.tasks.mexc_tasks_core import task_update_cost

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])
router.add_api_route("/15-min-job", task_update_cost, methods=["POST"])

__all__ = ["router"]
