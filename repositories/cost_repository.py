"""
Compatibility shim for CostRepository.
Delegates to repositories.account.cost_repository after repository layout split.
"""
from repositories.account.cost_repository import CostRepository

__all__ = ["CostRepository"]
