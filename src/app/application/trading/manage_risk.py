"""
Risk management use case shim.

Exports the legacy RiskService placeholder while migration progresses.
"""

from src.app.application.trading.services import RiskService

__all__ = ["RiskService"]
