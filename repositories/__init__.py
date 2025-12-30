"""Legacy repositories shim - redirects to src.app.infrastructure"""
from src.app.infrastructure.persistence.redis.repos import (
    PositionRepository,
    CostRepository,
    PriceRepository,
    TradeRepository,
)

__all__ = [
    "PositionRepository",
    "CostRepository",
    "PriceRepository",
    "TradeRepository",
]

