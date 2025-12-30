"""
Response parser placeholder for MEXC HTTP responses.

Keeps compatibility with the target layout while deferring to existing
response handling from the legacy client.
"""
from typing import Any, Dict


def passthrough(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return responses unchanged (legacy client already parses JSON)."""
    return payload


__all__ = ["passthrough"]
