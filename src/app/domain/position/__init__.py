"""
Domain Position Services (Legacy Compatibility)

⚠️ DEPRECATED: This module provides backward compatibility only.

New code should use:
    from src.app.domain.trading.services.position import PositionManager, PositionUpdater

This backward compatibility layer will be maintained for at least 2 major versions.
"""

import warnings

warnings.warn(
    "domain.position is deprecated. Use domain.trading.services.position instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.app.domain.trading.services.position.calculator import PositionManager
from src.app.domain.trading.services.position.updater import PositionUpdater

__all__ = ["PositionManager", "PositionUpdater"]

