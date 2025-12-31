"""
Compatibility shim for TradingBot.
Delegates to src.app.infrastructure.bot_runtime for new architecture.
"""
from src.app.infrastructure.bot_runtime import TradingBot

__all__ = ["TradingBot"]
