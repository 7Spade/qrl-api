"""
Account balance fetch shim using the migrated BalanceService.
"""
from src.app.application.account.balance_service import BalanceService
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client


async def get_balance() -> dict:
    service = BalanceService(mexc_client, redis_client)
    snapshot = await service.get_account_balance()
    BalanceService.to_usd_values(snapshot)
    return snapshot


__all__ = ["get_balance", "BalanceService"]
