"""
Environment shim referencing the shared config object.
"""

from src.app.infrastructure.config import config

__all__ = ["config"]
