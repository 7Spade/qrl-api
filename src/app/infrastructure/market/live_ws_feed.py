"""
Live WebSocket Feed - Real-time market data implementation

Implements MarketFeed port for live trading.
"""
from typing import AsyncIterator
from datetime import datetime

from src.app.domain.ports.market_feed import MarketFeed
from src.app.application.market.timeframe_aggregator import MarketCandle
from src.app.infrastructure.external.mexc.ws.ws_client import connect_public_trades


class LiveWSFeed(MarketFeed):
    """
    Live market data from MEXC WebSocket.
    
    From ✨.md Section 6.5: "LiveWSFeed for real-time WS data"
    """

    def __init__(self, symbol: str, interval: str = "1m"):
        """
        Initialize live WS feed.
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
            interval: Kline interval (default "1m")
        """
        self.symbol = symbol
        self.interval = interval

    async def stream(self) -> AsyncIterator[MarketCandle]:
        """
        Stream live market candles from MEXC WebSocket.
        
        Yields:
            MarketCandle instances from live data
        """
        async for raw_data in connect_public_trades(self.symbol, self.interval):
            # Map raw MEXC data to MarketCandle
            if isinstance(raw_data, dict) and "k" in raw_data:
                kline = raw_data["k"]
                candle = MarketCandle(
                    symbol=self.symbol,
                    open=float(kline.get("o", 0)),
                    high=float(kline.get("h", 0)),
                    low=float(kline.get("l", 0)),
                    close=float(kline.get("c", 0)),
                    volume=float(kline.get("v", 0)),
                    closed_at=datetime.fromtimestamp(kline.get("t", 0) / 1000),
                )
                yield candle


__all__ = ["LiveWSFeed"]
