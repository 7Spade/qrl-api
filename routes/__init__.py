"""
API Routes for QRL Trading API
"""
from routes.health import router as health_router
from routes.market import router as market_router
from routes.account import router as account_router
from routes.trading import router as trading_router


def register_routers(app):
    """
    Register all routers with the FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    # Register routers (health router is registered at root level, no prefix)
    app.include_router(health_router)
    app.include_router(market_router)
    app.include_router(account_router)
    app.include_router(trading_router)


__all__ = [
    'health_router',
    'market_router',
    'account_router',
    'trading_router',
    'register_routers'
]
