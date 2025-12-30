import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD_PATH = ROOT / "architecture_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("architecture_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load architecture_guard from {GUARD_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_architecture_guard_src_app_has_no_violations():
    guard = _load_guard()
    base = ROOT / "src" / "app"
    ok, violations = guard.check_architecture(base)
    assert ok, f"Expected no architecture guard violations, got: {violations}"
