"""
Redis account balance repository shim.

Re-exports the legacy BalanceCacheMixin to preserve behavior.
"""

from infrastructure.external.redis_client.balance_cache import BalanceCacheMixin

__all__ = ["BalanceCacheMixin"]
