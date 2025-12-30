"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._price_resolver import PriceResolver

__all__ = ["PriceResolver"]

