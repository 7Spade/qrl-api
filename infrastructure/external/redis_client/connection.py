"""Sync Redis connection placeholder to match documented layout."""
try:
    from redis import Connection  # type: ignore
except Exception:  # pragma: no cover - optional redis import
    Connection = object

__all__ = ["Connection"]
