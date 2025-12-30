import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_tasks_router_exposes_expected_paths():
    pytest.importorskip("httpx")
    from src.app.interfaces.tasks.router import router

    paths = {route.path for route in router.routes}
    assert "/tasks/01-min-job" in paths
    assert "/tasks/05-min-job" in paths
    assert "/tasks/15-min-job" in paths
