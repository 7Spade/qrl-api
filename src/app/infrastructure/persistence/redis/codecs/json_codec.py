"""
Simple JSON codec shim to align with target redis layout.
"""
import json
from typing import Any, Dict


def dumps(payload: Dict[str, Any]) -> str:
    return json.dumps(payload)


def loads(payload: str) -> Dict[str, Any]:
    return json.loads(payload)


__all__ = ["dumps", "loads"]
