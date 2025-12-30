"""
Key definitions for account-related Redis entries.
"""

ACCOUNT_BALANCE = "mexc:account_balance"
ACCOUNT_BALANCE_CACHE = "mexc:account_balance:cache"
ACCOUNT_TOTAL_VALUE = "mexc:total_value"
ACCOUNT_QRL_PRICE = "mexc:qrl_price"

__all__ = [
    "ACCOUNT_BALANCE",
    "ACCOUNT_BALANCE_CACHE",
    "ACCOUNT_TOTAL_VALUE",
    "ACCOUNT_QRL_PRICE",
]
