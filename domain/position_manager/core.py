"""
Position management domain logic (compatibility shim).

The canonical implementation now lives under `src/app/domain/position`.
This module subclasses it to preserve import paths and module names for
existing callers and tests.
"""

from src.app.domain.position.calculator import PositionManager as _PositionManager


class PositionManager(_PositionManager):
    """Compatibility wrapper for the migrated PositionManager."""


__all__ = ["PositionManager"]
