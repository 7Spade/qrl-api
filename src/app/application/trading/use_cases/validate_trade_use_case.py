"""
Trade validation use case shim.

Exports the legacy StrategyService placeholder for compatibility.
"""

from src.app.application.trading.services import StrategyService

__all__ = ["StrategyService"]
