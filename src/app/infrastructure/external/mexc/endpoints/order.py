"""Order endpoints wrapper."""
from src.app.infrastructure.external.mexc.trade_repo import TradeRepoMixin

OrderEndpoints = TradeRepoMixin

__all__ = ["OrderEndpoints"]
