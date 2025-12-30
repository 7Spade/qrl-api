"""Base RESP parser abstraction (placeholder for future implementations)."""


class BaseParser:
    """Define minimal interface for RESP parsers."""

    def parse(self, data):
        raise NotImplementedError("Parser not implemented")


__all__ = ["BaseParser"]
