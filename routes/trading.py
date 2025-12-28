"""
Trading Execution and Bot Control Routes
"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks

from models.requests import ControlRequest, ExecuteRequest
from models.responses import ExecuteResponse
from config import config
from mexc_client import mexc_client
from redis_client import redis_client
from bot import TradingBot

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Trading"])


@router.post("/control")
async def control_bot(request: ControlRequest):
    """
    Control bot execution (start, pause, stop)
    """
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    action = request.action.lower()
    reason = request.reason or "Manual control"
    
    if action not in ["start", "pause", "stop"]:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    
    # Update bot status in Redis
    await redis_client.set_bot_status(action, {
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })
    
    logger.info(f"Bot control: {action} - {reason}")
    
    return {
        "success": True,
        "action": action,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/execute", response_model=ExecuteResponse)
async def execute_trading(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute trading cycle
    
    This endpoint triggers a complete trading cycle execution using the bot's 6-phase system.
    It can run in foreground (immediate response) or background (async execution).
    """
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    # Initialize trading bot
    symbol = config.TRADING_SYMBOL
    dry_run = request.dry_run
    
    logger.info(f"Trading execution requested - Symbol: {symbol}, Dry Run: {dry_run}")
    
    try:
        # Create bot instance
        bot = TradingBot(mexc_client, redis_client, symbol, dry_run)
        
        # Execute trading cycle
        result = await bot.execute_cycle()
        
        return ExecuteResponse(
            success=result.get("success", False),
            action=result.get("action"),
            message=result.get("message", "Trading cycle completed"),
            details=result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Trading execution failed: {e}", exc_info=True)
        return ExecuteResponse(
            success=False,
            action=None,
            message=f"Trading execution failed: {str(e)}",
            details={"error": str(e)},
            timestamp=datetime.now().isoformat()
        )
