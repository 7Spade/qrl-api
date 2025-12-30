"""
Trading workflow use case shim.

Re-exports the legacy TradingWorkflow used by TradingService.
"""

from services.trading.trading_workflow import TradingWorkflow

__all__ = ["TradingWorkflow"]
