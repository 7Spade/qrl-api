"""
Compatibility shim for PositionRepository.
Delegates to repositories.account.position_repository after repository layout split.
"""
from repositories.account.position_repository import PositionRepository

__all__ = ["PositionRepository"]
