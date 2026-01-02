"""
Domain Position Services (Legacy Compatibility)

This package now re-exports from domain.trading for backward compatibility.
New code should import directly from src.app.domain.trading.services.position.
"""

from src.app.domain.trading.services.position.calculator import PositionManager
from src.app.domain.trading.services.position.updater import PositionUpdater

__all__ = ["PositionManager", "PositionUpdater"]

