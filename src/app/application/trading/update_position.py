"""
Position update use case shim.

Re-exports the PositionUpdater used by the legacy trading workflow.
"""

from services.trading.position_updater import PositionUpdater

__all__ = ["PositionUpdater"]
