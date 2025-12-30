"""
Shared ID helpers.
"""
from uuid import uuid4


def new_uuid() -> str:
    """Return a random UUID string."""
    return str(uuid4())


__all__ = ["new_uuid"]
