"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._strategy_service import StrategyService

__all__ = ["StrategyService"]

