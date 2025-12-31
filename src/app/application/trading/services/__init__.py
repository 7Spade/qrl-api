"""
Trading services - re-exports from legacy services.

This adapter allows application code to import trading services without
depending on root-level services directly.
"""
from src.app.application.trading.services import TradingService
from src.app.application.trading.services import RiskService
from src.app.application.trading.services import PositionUpdater
from src.app.application.trading.services import StrategyService
from src.app.application.trading.services import TradingWorkflow

__all__ = [
    "TradingService",
    "RiskService",
    "PositionUpdater",
    "StrategyService",
    "TradingWorkflow",
]
