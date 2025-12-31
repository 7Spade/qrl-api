"""
Compatibility wrapper: BalanceService now lives in
`src.app.application.account.balance_service`.
"""

from src.app.application.account.balance_service import BalanceService

__all__ = ["BalanceService"]
