"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._workflow import TradingWorkflow

__all__ = ["TradingWorkflow"]

