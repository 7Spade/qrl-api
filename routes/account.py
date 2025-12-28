"""
Account Management Routes
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from config import config
from mexc_client import mexc_client
from redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/balance")
async def get_account_balance():
    """
    Get account balance (requires API keys)
    
    Fetches real-time balance from MEXC API and stores in Redis permanently.
    Requires valid MEXC_API_KEY and MEXC_SECRET_KEY with spot trading permissions.
    """
    # Validate API keys are configured
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        logger.error("API keys not configured - cannot fetch account balance")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                "help": "Check Cloud Run environment variables or .env file"
            }
        )
    
    try:
        logger.info("Fetching account balance from MEXC API")
        
        # Fetch account info from MEXC
        account_info = await mexc_client.get_account_info()
        logger.info(f"Received account info with {len(account_info.get('balances', []))} assets")
        
        # Store raw response in Redis (PERMANENT)
        await redis_client.set_mexc_raw_response("account_info", account_info)
        logger.info("✓ Raw response stored in Redis")
        
        # Extract QRL and USDT balances
        balances = {}
        all_assets = []
        
        for balance in account_info.get("balances", []):
            asset = balance.get("asset")
            all_assets.append(asset)
            
            if asset in ["QRL", "USDT"]:
                balances[asset] = {
                    "free": balance.get("free", "0"),
                    "locked": balance.get("locked", "0"),
                    "total": str(float(balance.get("free", "0")) + float(balance.get("locked", "0")))
                }
        
        # Ensure QRL and USDT are always in response
        if "QRL" not in balances:
            balances["QRL"] = {"free": "0", "locked": "0", "total": "0"}
        if "USDT" not in balances:
            balances["USDT"] = {"free": "0", "locked": "0", "total": "0"}
        
        # Fetch QRL price
        try:
            price_data = await mexc_client.get_ticker_price(config.TRADING_SYMBOL)
            qrl_price = float(price_data.get("price", "0"))
            await redis_client.set_mexc_qrl_price(qrl_price, price_data)
        except Exception as price_error:
            logger.warning(f"Failed to fetch QRL price: {price_error}")
            qrl_price = 0
            price_data = {}
        
        # Calculate total value in USDT
        qrl_total = float(balances["QRL"]["total"])
        usdt_total = float(balances["USDT"]["total"])
        qrl_value_usdt = qrl_total * qrl_price
        total_value_usdt = qrl_value_usdt + usdt_total
        
        value_breakdown = {
            "qrl_quantity": qrl_total,
            "qrl_price_usdt": qrl_price,
            "qrl_value_usdt": qrl_value_usdt,
            "usdt_balance": usdt_total,
            "total_value_usdt": total_value_usdt
        }
        
        # Store data in Redis (PERMANENT)
        await redis_client.set_mexc_total_value(total_value_usdt, value_breakdown)
        balance_data = {
            "QRL": balances["QRL"],
            "USDT": balances["USDT"],
            "all_assets_count": len(all_assets)
        }
        await redis_client.set_mexc_account_balance(balance_data)
        
        logger.info(f"Total value: {total_value_usdt} USDT")
        
        # Return comprehensive response
        return {
            "success": True,
            "balances": balances,
            "qrl_price": qrl_price,
            "total_value": {
                "usdt": total_value_usdt,
                "breakdown": value_breakdown
            },
            "timestamp": datetime.now().isoformat(),
            "redis_storage": {
                "raw_response": "mexc:raw_response:account_info",
                "account_balance": "mexc:account_balance",
                "qrl_price": "mexc:qrl_price",
                "total_value": "mexc:total_value"
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching account balance: {e}", exc_info=True)
        
        # Check if it's an authentication error
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg or "invalid" in error_msg:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "API keys may be invalid or lack spot trading permissions",
                    "help": "Verify your MEXC API keys and ensure they have SPOT trading enabled",
                    "technical_details": str(e)
                }
            )
        
        # Generic error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch account balance",
                "message": str(e),
                "help": "Check MEXC API status and your API key permissions"
            }
        )


@router.get("/balance/redis")
async def get_account_balance_from_redis():
    """
    Get cached account balance from Redis
    
    Returns the most recent balance data stored in Redis.
    Useful for quick access without making MEXC API calls.
    """
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    try:
        # Get cached data from Redis
        account_balance = await redis_client.get_mexc_account_balance()
        qrl_price = await redis_client.get_mexc_qrl_price()
        total_value = await redis_client.get_mexc_total_value()
        
        if not account_balance:
            raise HTTPException(
                status_code=404,
                detail="No cached balance data available. Call /account/balance first."
            )
        
        return {
            "success": True,
            "balances": account_balance,
            "qrl_price": qrl_price.get("price") if qrl_price else None,
            "total_value": total_value,
            "cached": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance from Redis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch balance from Redis: {str(e)}"
        )


@router.get("/sub-accounts")
async def get_sub_accounts():
    """
    Get list of sub-accounts
    
    Supports both Spot API and Broker API modes based on SUB_ACCOUNT_MODE config.
    Returns sub-account list in a unified format.
    """
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        return {
            "mode": config.SUB_ACCOUNT_MODE,
            "sub_accounts": [],
            "message": "API keys not configured",
            "help": "Set MEXC_API_KEY and MEXC_SECRET_KEY to view sub-accounts"
        }
    
    try:
        # Use unified interface (automatically selects Spot or Broker API)
        sub_accounts = await mexc_client.get_sub_accounts()
        
        return {
            "mode": config.SUB_ACCOUNT_MODE,
            "sub_accounts": sub_accounts,
            "count": len(sub_accounts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sub-accounts: {e}")
        return {
            "mode": config.SUB_ACCOUNT_MODE,
            "sub_accounts": [],
            "error": str(e),
            "message": "Failed to fetch sub-accounts. Check API permissions.",
            "help": "Ensure your API keys have sub-account management permissions enabled."
        }


@router.get("/sub-account/balance")
async def get_sub_account_balance(
    identifier: str = Query(..., description="Sub-account ID (Spot) or Name (Broker)")
):
    """
    Get balance for a specific sub-account
    
    Args:
        identifier: Sub-account identifier (numeric ID for Spot, string name for Broker)
    """
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(status_code=401, detail="API keys not configured")
    
    try:
        # Use unified interface
        balance = await mexc_client.get_sub_account_balance(identifier)
        
        return {
            "mode": config.SUB_ACCOUNT_MODE,
            "identifier": identifier,
            "balance": balance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sub-account balance: {str(e)}"
        )


@router.post("/sub-account/transfer")
async def transfer_between_sub_accounts(
    from_account: str = Query(..., description="Source sub-account"),
    to_account: str = Query(..., description="Destination sub-account"),
    asset: str = Query(..., description="Asset symbol (e.g., USDT, QRL)"),
    amount: float = Query(..., description="Amount to transfer")
):
    """
    Transfer assets between sub-accounts
    
    Note: API implementation varies between Spot and Broker modes
    """
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(status_code=401, detail="API keys not configured")
    
    try:
        # Implementation depends on mode (Spot vs Broker)
        if config.is_broker_mode:
            # Broker API transfer
            result = await mexc_client.broker_transfer_between_sub_accounts(
                from_account, to_account, asset, amount
            )
        else:
            # Spot API transfer
            result = await mexc_client.transfer_between_sub_accounts(
                from_account, to_account, asset, amount
            )
        
        return {
            "success": True,
            "mode": config.SUB_ACCOUNT_MODE,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Sub-account transfer failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transfer failed: {str(e)}"
        )
