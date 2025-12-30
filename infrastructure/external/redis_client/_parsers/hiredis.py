"""Hiredis parser wrapper placeholder."""
try:
    from redis.connection import HiredisParser as RedisHiredisParser  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    RedisHiredisParser = None

from .base import BaseParser


class HiredisParserWrapper(BaseParser):
    """Expose hiredis parser when installed; otherwise no-op."""

    def __init__(self):
        self._parser = RedisHiredisParser() if RedisHiredisParser else None

    def parse(self, data):
        if self._parser:
            return self._parser.parse(data)
        return data


__all__ = ["HiredisParserWrapper", "RedisHiredisParser"]
