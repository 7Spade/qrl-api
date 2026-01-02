"""
Domain Risk Services (Legacy Compatibility)

This package now re-exports from domain.trading for backward compatibility.
New code should import directly from src.app.domain.trading.services.risk.
"""

from src.app.domain.trading.services.risk.limits import RiskManager
from src.app.domain.trading.services.risk.stop_loss import StopLossGuard

__all__ = ["RiskManager", "StopLossGuard"]

