"""Socket-level RESP parser placeholder."""
from .base import BaseParser


class SocketParser(BaseParser):
    """Placeholder socket parser; delegate to redis-py parser in future."""

    def parse(self, data):
        return data


__all__ = ["SocketParser"]
