"""
Core balance service - Manages account balance operations.
"""

from src.app.infrastructure.external import mexc_client, redis_client
from src.app.domain.trading.entities.account import Account
import logging

logger = logging.getLogger(__name__)


class BalanceService:
    """Service for managing account balance operations."""
    
    def __init__(self):
        self.mexc = mexc_client
        self.redis = redis_client
    
    async def get_account_balance(self) -> Account:
        """Get current account balance from MEXC."""
        # Implementation moved here from old application.account.balance_service
        balance_data = await self.mexc.get_account_info()
        return Account(
            qrl_balance=float(balance_data.get("QRL", {}).get("free", 0)),
            usdt_balance=float(balance_data.get("USDT", {}).get("free", 0))
        )


__all__ = ["BalanceService"]
