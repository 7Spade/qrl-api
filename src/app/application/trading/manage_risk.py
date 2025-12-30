"""
Risk management use case shim.

Exports the legacy RiskService placeholder while migration progresses.
"""

from services.trading.risk_service import RiskService

__all__ = ["RiskService"]
