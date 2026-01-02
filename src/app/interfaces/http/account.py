"""
Account HTTP routes aligned to target architecture.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.use_cases.get_orders_use_case import get_orders
from src.app.application.trading.use_cases.get_trades_use_case import get_trades
from src.app.application.trading.services.trading.rebalance_service import RebalanceService
from src.app.application.trading.services.trading.intelligent_rebalance_service import IntelligentRebalanceService

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from src.app.infrastructure.external import mexc_client
    from src.app.infrastructure.external import redis_client
    return BalanceService(mexc_client, redis_client, cache_ttl=45)


def _get_mexc_client():
    from src.app.infrastructure.external import mexc_client
    return mexc_client


def _has_credentials(mexc_client) -> bool:
    settings = getattr(mexc_client, "settings", None)
    return bool(getattr(settings, "api_key", None) and getattr(settings, "secret_key", None))


async def _cache_orders(payload):
    try:
        from src.app.infrastructure.external import redis_client

        if not redis_client.connected:
            await redis_client.connect()
        await redis_client.set_mexc_raw_response("openOrders", payload)
    except Exception as exc:
        logger.warning(f"Failed to cache orders: {exc}")
        return False
    return True


async def _get_cached_orders():
    try:
        from src.app.infrastructure.external import redis_client

        if not redis_client.connected:
            await redis_client.connect()
        cached = await redis_client.get_mexc_raw_response("openOrders")
        if cached:
            orders = cached.get("orders") or cached.get("data") or []
            return {
                "success": True,
                "source": "cache",
                "symbol": cached.get("symbol") or "QRLUSDT",
                "orders": orders,
                "count": len(orders),
                "timestamp": datetime.now().isoformat(),
                "note": "served from cache",
            }
    except Exception as exc:
        logger.warning(f"Failed to load cached orders: {exc}")
    return None


@router.get("/balance")
async def get_account_balance():
    """Get account balance with fallback to cached snapshot."""
    try:
        service = _build_balance_service()
        snapshot = await service.get_account_balance()
        BalanceService.to_usd_values(snapshot)
        return snapshot
    except ValueError as exc:
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/balance/cache")
async def get_cached_balance():
    """Retrieve cached balance without hitting the exchange."""
    from src.app.infrastructure.external import redis_client

    cached = await redis_client.get_cached_account_balance()
    if cached:
        cached["source"] = "cache"
        cached["timestamp"] = datetime.now().isoformat()
        return cached
    raise HTTPException(status_code=404, detail="No cached balance available")


@router.get("/orders")
async def orders_endpoint():
    """Get user's open orders for QRL/USDT (real-time from MEXC API)."""
    mexc_client = _get_mexc_client()

    try:
        from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL

        if not _has_credentials(mexc_client):
            cached = await _get_cached_orders()
            if cached:
                return cached
            return {
                "success": True,
                "source": "cache",
                "symbol": QRL_USDT_SYMBOL,
                "orders": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
                "note": "API credentials missing; returning empty orders",
            }

        result = await get_orders(QRL_USDT_SYMBOL, mexc_client)
        await _cache_orders(result)
        return result
    except Exception as e:
        logger.error(f"Failed to get orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def trades_endpoint(symbol: str = "QRLUSDT", limit: int = 50):
    """Get user's trade history (real-time from MEXC API)."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_trades(symbol, mexc_client, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to get trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders")
async def place_order_endpoint(
    symbol: str = "QRLUSDT",
    side: str = "BUY",
    order_type: str = "MARKET",
    quantity: float = None,
    price: float = None,
):
    """
    Place a new order on MEXC exchange.
    
    Args:
        symbol: Trading pair (default: QRLUSDT)
        side: BUY or SELL
        order_type: MARKET or LIMIT
        quantity: Order quantity (required for MARKET, optional for LIMIT)
        price: Order price (required for LIMIT orders)
    
    Returns:
        Order response from MEXC API with order details
    """
    try:
        mexc_client = _get_mexc_client()
        
        if not _has_credentials(mexc_client):
            raise HTTPException(
                status_code=401,
                detail="API credentials required for placing orders"
            )
        
        # Validate required parameters
        if order_type.upper() == "MARKET" and not quantity:
            raise HTTPException(
                status_code=400,
                detail="Quantity is required for market orders"
            )
        
        if order_type.upper() == "LIMIT" and (not quantity or not price):
            raise HTTPException(
                status_code=400,
                detail="Both quantity and price are required for limit orders"
            )
        
        logger.info(f"Placing {side} {order_type} order for {symbol}")
        
        async with mexc_client:
            # Prepare order parameters
            order_params = {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": order_type.upper(),
            }
            
            if quantity:
                order_params["quantity"] = quantity
            
            if price:
                order_params["price"] = price
            
            # Place order via MEXC API
            order_result = await mexc_client.create_order(**order_params)
            
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "order": order_result,
                "timestamp": datetime.now().isoformat(),
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-accounts")
async def get_configured_sub_account():
    """Get configured sub-account balance (alias for convenience)."""
    mexc_client = _get_mexc_client()
    from src.app.infrastructure.config import config

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(status_code=401, detail="API keys not configured")

        sub_account_id = config.active_sub_account_identifier
        if not sub_account_id:
            raise HTTPException(
                status_code=400,
                detail="Sub-account not configured - set SUB_ACCOUNT_ID or SUB_ACCOUNT_NAME",
            )

        async with mexc_client:
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            balance_data = await mexc_client.get_sub_account_balance(sub_account_id)
            logger.info(f"Retrieved sub-account balance for {sub_account_id}")
            return {
                "success": True,
                "mode": mode,
                "sub_account_id": sub_account_id,
                "balance": balance_data,
                "timestamp": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalance/symmetric")
async def rebalance_symmetric_endpoint():
    """
    Generate symmetric (50/50 value) rebalance plan and execute order.
    
    This endpoint provides manual rebalancing without requiring Cloud Scheduler authentication.
    
    Workflow:
    1. Generates rebalance plan based on account balance
    2. If action is BUY or SELL (not HOLD), executes market order on MEXC
    3. Returns plan and order execution results
    
    Returns:
        dict: Rebalance plan with action (HOLD/BUY/SELL), order execution results
        
    Raises:
        401: API credentials not configured
        500: Rebalancing failed
    """
    mexc_client = _get_mexc_client()
    
    # Check credentials
    if not _has_credentials(mexc_client):
        raise HTTPException(status_code=401, detail="API credentials not configured")
    
    try:
        # Get Redis client
        from src.app.infrastructure.external import redis_client, QRL_USDT_SYMBOL
        
        # Connect Redis if available
        redis_available = False
        if redis_client and not redis_client.connected:
            try:
                await redis_client.connect()
                redis_available = redis_client.connected
            except Exception:
                redis_available = False
        elif redis_client:
            redis_available = redis_client.connected
        
        # Generate rebalance plan
        balance_service = BalanceService(mexc_client, redis_client, cache_ttl=45)
        rebalance_service = RebalanceService(balance_service, redis_client)
        plan = await rebalance_service.generate_plan()
        
        logger.info(
            f"[rebalance-symmetric-http] Plan generated - "
            f"Action: {plan.get('action')}, "
            f"Quantity: {plan.get('quantity', 0):.4f}"
        )
        
        # Execute order if action is BUY or SELL
        order_result = None
        if plan.get("action") in ["BUY", "SELL"]:
            try:
                logger.info(
                    f"[rebalance-symmetric-http] Executing {plan['action']} order - "
                    f"Quantity: {plan['quantity']:.4f} QRL"
                )
                async with mexc_client:
                    order = await mexc_client.place_market_order(
                        symbol=QRL_USDT_SYMBOL,
                        side=plan["action"],
                        quantity=plan["quantity"],
                    )
                order_result = {
                    "executed": True,
                    "order_id": order.get("orderId"),
                    "status": order.get("status"),
                    "details": order,
                }
                logger.info(
                    f"[rebalance-symmetric-http] Order executed successfully - "
                    f"Order ID: {order.get('orderId')}"
                )
            except Exception as exc:
                order_result = {
                    "executed": False,
                    "error": str(exc),
                }
                logger.error(f"[rebalance-symmetric-http] Order execution failed: {exc}")
        
        return {
            "success": True,
            "strategy": "symmetric",
            "redis_available": redis_available,
            "plan": plan,
            "order": order_result,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"[rebalance-symmetric-http] Failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/rebalance/intelligent")
async def rebalance_intelligent_endpoint():
    """
    Generate intelligent rebalance plan with MA signals and execute order.
    
    This endpoint provides manual intelligent rebalancing without requiring Cloud Scheduler authentication.
    
    Enhanced rebalancing strategy that includes:
    - MA (Moving Average) cross signal detection (MA_7 vs MA_25)
    - Cost basis validation (buy low, sell high)
    - Position tier management (70% core, 20% swing, 10% active)
    - Automatic order execution when conditions are met
    
    Decision logic:
    - BUY: Golden cross (MA_7 > MA_25) + price <= cost_avg
    - SELL: Death cross (MA_7 < MA_25) + price >= cost_avg * 1.03
    - HOLD: Otherwise or when within threshold
    
    Returns:
        dict: Intelligent rebalance plan with:
            - action: HOLD/BUY/SELL
            - ma_indicators: MA signals and analysis
            - position_tiers: core, swing, active positions
            - order: execution results (if BUY/SELL)
            
    Raises:
        401: API credentials not configured
        500: Rebalancing failed
    """
    mexc_client = _get_mexc_client()
    
    # Check credentials
    if not _has_credentials(mexc_client):
        raise HTTPException(status_code=401, detail="API credentials not configured")
    
    try:
        # Get Redis client
        from src.app.infrastructure.external import redis_client, QRL_USDT_SYMBOL
        
        # Connect Redis if available
        redis_available = False
        if redis_client and not redis_client.connected:
            try:
                await redis_client.connect()
                redis_available = redis_client.connected
            except Exception:
                redis_available = False
        elif redis_client:
            redis_available = redis_client.connected
        
        # Generate intelligent rebalance plan
        balance_service = BalanceService(mexc_client, redis_client, cache_ttl=45)
        intelligent_service = IntelligentRebalanceService(
            balance_service=balance_service,
            mexc_client=mexc_client,
            redis_client=redis_client,
        )
        plan = await intelligent_service.generate_plan()
        
        logger.info(
            f"[rebalance-intelligent-http] Plan generated - "
            f"Action: {plan.get('action')}, "
            f"Quantity: {plan.get('quantity', 0):.4f}, "
            f"MA Signal: {plan.get('ma_indicators', {}).get('signal', 'N/A')}"
        )
        
        # Execute order if action is BUY or SELL
        order_result = None
        if plan.get("action") in ["BUY", "SELL"]:
            try:
                logger.info(
                    f"[rebalance-intelligent-http] Executing {plan['action']} order - "
                    f"Quantity: {plan['quantity']:.4f} QRL"
                )
                async with mexc_client:
                    order = await mexc_client.place_market_order(
                        symbol=QRL_USDT_SYMBOL,
                        side=plan["action"],
                        quantity=plan["quantity"],
                    )
                order_result = {
                    "executed": True,
                    "order_id": order.get("orderId"),
                    "status": order.get("status"),
                    "details": order,
                }
                logger.info(
                    f"[rebalance-intelligent-http] Order executed successfully - "
                    f"Order ID: {order.get('orderId')}"
                )
            except Exception as exc:
                order_result = {
                    "executed": False,
                    "error": str(exc),
                }
                logger.error(f"[rebalance-intelligent-http] Order execution failed: {exc}")
        
        return {
            "success": True,
            "strategy": "intelligent",
            "redis_available": redis_available,
            "plan": plan,
            "order": order_result,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"[rebalance-intelligent-http] Failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router"]
