"""
Application Trading Use Cases

This module contains use case implementations for the trading application.
Use cases represent the application-specific business rules and orchestrate the flow
of data to and from entities, coordinating the work of domain services.

Use Case Characteristics:
- Orchestrate domain logic without containing business rules
- Depend on ports (interfaces) not concrete implementations
- Are the entry points for features from the interface layer
- Handle cross-cutting concerns (transactions, logging, validation)

Use Cases in this module:
- execute_trade_use_case: Execute trading operations
- manage_risk_use_case: Manage risk and limits
- update_position_use_case: Update position information  
- validate_trade_use_case: Validate trade parameters
- trading_workflow: Coordinate complex trading workflows

Note: These are currently shims/re-exports for backward compatibility.
They will be converted to proper use case implementations in future refactoring.
"""

from src.app.application.trading.use_cases.execute_trade_use_case import *
from src.app.application.trading.use_cases.manage_risk_use_case import *
from src.app.application.trading.use_cases.update_position_use_case import *
from src.app.application.trading.use_cases.validate_trade_use_case import *
from src.app.application.trading.use_cases.trading_workflow import *

__all__ = [
    "TradingService",
    "RiskManager",
    "PositionUpdater",
    "TradeValidator",
    "TradingWorkflow",
]
