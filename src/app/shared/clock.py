"""
Shared clock utilities.
"""
from datetime import datetime, timezone


def now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


__all__ = ["now_iso"]
