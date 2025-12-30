"""
Aggregate mixin combining account and price caching helpers.
"""
from .balance_account_cache import AccountBalanceCacheMixin
from .balance_price_cache import BalancePriceCacheMixin


class BalanceCacheMixin(AccountBalanceCacheMixin, BalancePriceCacheMixin):
    """Backwards-compatible aggregate mixin."""


__all__ = ["BalanceCacheMixin", "AccountBalanceCacheMixin", "BalancePriceCacheMixin"]
