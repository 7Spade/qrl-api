"""Sync Redis connection pool placeholder matching README structure."""
try:
    from redis import ConnectionPool  # type: ignore
except Exception:  # pragma: no cover
    ConnectionPool = object

__all__ = ["ConnectionPool"]
