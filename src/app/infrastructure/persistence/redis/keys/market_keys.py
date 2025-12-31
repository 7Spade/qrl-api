"""
Key definitions for market-related Redis entries.
"""

TICKER_KEY = "market:ticker:{symbol}"
ORDERBOOK_KEY = "market:orderbook:{symbol}"
TRADES_KEY = "market:trades:{symbol}"
KLINES_KEY = "market:klines:{symbol}:{interval}"

__all__ = ["TICKER_KEY", "ORDERBOOK_KEY", "TRADES_KEY", "KLINES_KEY"]
