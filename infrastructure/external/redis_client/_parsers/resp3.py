"""Python RESP3 parser placeholder."""
from .base import BaseParser


class Resp3Parser(BaseParser):
    def parse(self, data):
        return data


__all__ = ["Resp3Parser"]
