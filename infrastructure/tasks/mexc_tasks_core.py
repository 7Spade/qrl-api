"""
Task router aggregator: include split job routers for clarity.
"""
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])

# import split job routers and include
from .job_01_min import router as router_01
from .job_05_min import router as router_05
from .job_15_min import router as router_15

router.include_router(router_01)
router.include_router(router_05)
router.include_router(router_15)
