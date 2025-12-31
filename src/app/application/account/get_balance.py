"""
Account balance use case shim.

Exposes the BalanceService implementation from the application layer.
"""

from src.app.application.account.balance_service import BalanceService

__all__ = ["BalanceService"]
