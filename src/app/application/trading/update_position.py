"""
Position update use case shim.

Re-exports the PositionUpdater used by the legacy trading workflow.
"""

from src.app.application.trading.services import PositionUpdater

__all__ = ["PositionUpdater"]
