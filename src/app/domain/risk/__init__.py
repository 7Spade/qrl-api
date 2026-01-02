"""
Domain Risk Services (Legacy Compatibility)

⚠️ DEPRECATED: This module provides backward compatibility only.

New code should use:
    from src.app.domain.trading.services.risk import RiskManager, StopLossGuard

This backward compatibility layer will be maintained for at least 2 major versions.
"""

import warnings

warnings.warn(
    "domain.risk is deprecated. Use domain.trading.services.risk instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.app.domain.trading.services.risk.limits import RiskManager
from src.app.domain.trading.services.risk.stop_loss import StopLossGuard

__all__ = ["RiskManager", "StopLossGuard"]

