"""Parser helpers for Redis RESP decoding (minimal placeholder layer)."""
try:
    from redis.connection import HiredisParser  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    HiredisParser = None


def hiredis_parser_kwargs():
    """
    Provide parser kwargs for redis.asyncio ConnectionPool using hiredis when available.
    """
    return {"parser_class": HiredisParser} if HiredisParser else {}


__all__ = ["HiredisParser", "hiredis_parser_kwargs"]
