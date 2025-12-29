"""
Compatibility shim for PriceRepository.
Delegates to repositories.market.price_repository after repository layout split.
"""
from repositories.market.price_repository import PriceRepository

__all__ = ["PriceRepository"]
