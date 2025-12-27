"""
Cloud Scheduler Tasks for Google Cloud Run
HTTP endpoints triggered by Google Cloud Scheduler
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException

from config import config
from mexc_client import mexc_client
from redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/sync-balance")
async def task_sync_balance(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """
    Cloud Scheduler Task: Sync MEXC account balance to Redis
    Triggered by: Cloud Scheduler (every 1-5 minutes)
    """
    # Verify request is from Cloud Scheduler
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            return {"status": "skipped", "reason": "API keys not configured"}
        
        async with mexc_client:
            account_info = await mexc_client.get_account_info()
            
            qrl_balance = 0.0
            usdt_balance = 0.0
            
            for balance in account_info.get("balances", []):
                asset = balance.get("asset")
                if asset == "QRL":
                    qrl_balance = float(balance.get("free", 0))
                elif asset == "USDT":
                    usdt_balance = float(balance.get("free", 0))
            
            # Update Redis
            await redis_client.set_position({
                "qrl_balance": str(qrl_balance),
                "usdt_balance": str(usdt_balance),
                "updated_at": datetime.now().isoformat()
            })
            
            logger.info(f"[Cloud Task] Balance synced: QRL={qrl_balance:.4f}, USDT={usdt_balance:.2f}")
            
            return {
                "status": "success",
                "task": "sync-balance",
                "qrl_balance": qrl_balance,
                "usdt_balance": usdt_balance,
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Balance sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-price")
async def task_update_price(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """
    Cloud Scheduler Task: Update QRL/USDT price
    Triggered by: Cloud Scheduler (every 1 minute)
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    try:
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            
            await redis_client.set_latest_price(price, volume_24h)
            await redis_client.add_price_to_history(price)
            
            logger.info(f"[Cloud Task] Price updated: {price:.6f}")
            
            return {
                "status": "success",
                "task": "update-price",
                "price": price,
                "volume_24h": volume_24h,
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Price update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-cost")
async def task_update_cost(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """
    Cloud Scheduler Task: Update cost and PnL data
    Triggered by: Cloud Scheduler (every 5 minutes)
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    try:
        position = await redis_client.get_position()
        cost_data = await redis_client.get_cost_data()
        
        qrl_balance = float(position.get("qrl_balance", 0))
        avg_cost = float(cost_data.get("avg_cost", 0))
        
        if qrl_balance > 0 and avg_cost > 0:
            async with mexc_client:
                ticker = await mexc_client.get_ticker_price("QRLUSDT")
                current_price = float(ticker.get("price", 0))
            
            unrealized_pnl = (current_price - avg_cost) * qrl_balance
            total_invested = avg_cost * qrl_balance
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            
            await redis_client.set_cost_data(
                avg_cost=avg_cost,
                total_invested=total_invested,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl
            )
            
            logger.info(f"[Cloud Task] Cost updated: unrealized_pnl={unrealized_pnl:.2f}")
            
            return {
                "status": "success",
                "task": "update-cost",
                "unrealized_pnl": unrealized_pnl,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat()
            }
        
        return {"status": "skipped", "reason": "No position or cost data"}
    
    except Exception as e:
        logger.error(f"[Cloud Task] Cost update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
