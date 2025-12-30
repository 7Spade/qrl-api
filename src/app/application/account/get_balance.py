"""
Account balance use case shim.

Exposes the legacy BalanceService from `services.account` so the new
application layer can depend on it without changing behavior.
"""

from services.account.balance_service_core import BalanceService

__all__ = ["BalanceService"]
