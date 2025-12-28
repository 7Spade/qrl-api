"""
API Routes for QRL Trading API
"""
from routes.health import router as health_router
from routes.market import router as market_router
from routes.account import router as account_router
from routes.trading import router as trading_router

__all__ = [
    'health_router',
    'market_router',
    'account_router',
    'trading_router'
]
