"""Python RESP2 parser placeholder."""
from .base import BaseParser


class Resp2Parser(BaseParser):
    def parse(self, data):
        return data


__all__ = ["Resp2Parser"]
