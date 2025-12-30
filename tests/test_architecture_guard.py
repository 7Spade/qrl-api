import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from architecture_guard import check_architecture


def test_architecture_guard_src_app_has_no_violations():
    base = Path(__file__).resolve().parent.parent / "src" / "app"
    ok, violations = check_architecture(base)
    assert ok, f"Expected no architecture guard violations, got: {violations}"
