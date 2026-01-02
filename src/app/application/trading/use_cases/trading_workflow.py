"""
Trading workflow use case shim.

Re-exports the legacy TradingWorkflow used by TradingService.
"""

from src.app.application.trading.services import TradingWorkflow

__all__ = ["TradingWorkflow"]
