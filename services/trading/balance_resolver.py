"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._balance_resolver import BalanceResolver

__all__ = ["BalanceResolver"]

