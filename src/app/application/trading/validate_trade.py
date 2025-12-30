"""
Trade validation use case shim.

Exports the legacy StrategyService placeholder for compatibility.
"""

from services.trading.strategy_service import StrategyService

__all__ = ["StrategyService"]
