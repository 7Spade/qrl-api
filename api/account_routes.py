"""
Account management API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/balance")
async def get_account_balance():
    """
    Get account balance (real-time from MEXC API)
    
    Returns:
        Account balance with QRL and USDT totals
    """
    from infrastructure.external.mexc_client import mexc_client
    
    try:
        async with mexc_client:
            # Get account info from MEXC
            account_info = await mexc_client.get_account_info()
            
            # Extract balances
            balances = account_info.get("balances", [])
            
            # Find QRL and USDT balances
            qrl_balance = {"asset": "QRL", "free": "0", "locked": "0"}
            usdt_balance = {"asset": "USDT", "free": "0", "locked": "0"}
            
            for balance in balances:
                if balance.get("asset") == "QRL":
                    qrl_balance = balance
                elif balance.get("asset") == "USDT":
                    usdt_balance = balance
            
            # Calculate totals
            qrl_total = float(qrl_balance.get("free", 0)) + float(qrl_balance.get("locked", 0))
            usdt_total = float(usdt_balance.get("free", 0)) + float(usdt_balance.get("locked", 0))
            
            logger.info(
                f"Account balance fetched - QRL: {qrl_total:.2f}, USDT: {usdt_total:.2f}"
            )
            
            return {
                "success": True,
                "source": "api",
                "balances": {
                    "QRL": {
                        "free": qrl_balance.get("free"),
                        "locked": qrl_balance.get("locked"),
                        "total": qrl_total
                    },
                    "USDT": {
                        "free": usdt_balance.get("free"),
                        "locked": usdt_balance.get("locked"),
                        "total": usdt_total
                    }
                },
                "account_type": account_info.get("accountType"),
                "can_trade": account_info.get("canTrade"),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/redis")
async def get_account_balance_from_redis():
    """
    Get account balance from Redis cache (may be stale)
    
    Returns:
        Cached position data from Redis
    """
    from infrastructure.external.redis_client import redis_client
    
    try:
        position = await redis_client.get_position()
        
        if not position:
            raise HTTPException(
                status_code=404,
                detail="No position data in Redis - run /tasks/sync-balance first"
            )
        
        logger.info("Position data retrieved from Redis")
        
        return {
            "success": True,
            "source": "redis",
            "position": position,
            "warning": "This data may be stale - use /account/balance for real-time data",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get position from Redis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-accounts")
async def get_sub_accounts():
    """
    Get configured sub-account information
    
    Note: In SPOT mode, the main account cannot query sub-account balances.
    Only BROKER mode supports querying sub-account balances from the main account.
    
    Returns:
        Configured sub-account information and guidance
    """
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.config.config import config
    
    try:
        # Check if API keys are configured
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            # Return configuration guidance without requiring API keys
            return {
                "success": False,
                "configured": False,
                "message": "API keys not configured",
                "help": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get configured sub-account identifier
        sub_account_id = config.active_sub_account_identifier
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        
        if not sub_account_id:
            return {
                "success": False,
                "configured": False,
                "mode": mode,
                "message": "Sub-account not configured",
                "help": {
                    "SPOT": "Set SUB_ACCOUNT_ID environment variable",
                    "BROKER": "Set SUB_ACCOUNT_NAME environment variable"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # SPOT mode: Cannot query balance from main account
        if mode == "SPOT":
            logger.info(f"Sub-account configured in SPOT mode: {sub_account_id}")
            return {
                "success": True,
                "configured": True,
                "mode": mode,
                "sub_account_id": sub_account_id,
                "message": "Sub-account configured successfully",
                "limitation": "SPOT API does not support querying sub-account balance from main account",
                "solution": "To query balance, use the sub-account's own API key (SUB_ACCOUNT_ID as MEXC_API_KEY)",
                "timestamp": datetime.now().isoformat()
            }
        
        # BROKER mode: Try to query balance
        async with mexc_client:
            try:
                balance_data = await mexc_client.get_sub_account_balance(sub_account_id)
                
                logger.info(f"Retrieved balance for sub-account: {sub_account_id} using {mode} API")
                
                return {
                    "success": True,
                    "configured": True,
                    "mode": mode,
                    "sub_account_id": sub_account_id,
                    "balance": balance_data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.warning(f"Failed to query sub-account balance in BROKER mode: {e}")
                return {
                    "success": False,
                    "configured": True,
                    "mode": mode,
                    "sub_account_id": sub_account_id,
                    "error": str(e),
                    "help": "Ensure your MEXC account has BROKER API permissions",
                    "timestamp": datetime.now().isoformat()
                }
    
    except Exception as e:
        logger.error(f"Unexpected error in sub-accounts endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
