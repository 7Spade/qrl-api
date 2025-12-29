"""
Compatibility shim for TradeRepository.
Delegates to repositories.trade.trade_repository after repository layout split.
"""
from repositories.trade.trade_repository import TradeRepository

__all__ = ["TradeRepository"]
