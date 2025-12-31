"""
Redis account balance repository shim.

Re-exports the legacy BalanceCacheMixin to preserve behavior.
"""

from src.app.infrastructure.persistence.redis.balance_cache import BalanceCacheMixin

__all__ = ["BalanceCacheMixin"]
