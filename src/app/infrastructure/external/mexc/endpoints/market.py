"""Market endpoints wrapper."""
from src.app.infrastructure.external.mexc.market_endpoints import MarketEndpointsMixin

MarketEndpoints = MarketEndpointsMixin

__all__ = ["MarketEndpoints"]
