"""
APScheduler-based Task Scheduler for QRL Trading Bot
Implements scheduled tasks for automated system maintenance
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import config
from mexc_client import mexc_client
from redis_client import redis_client

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Trading bot scheduler manager"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False
    
    async def start(self):
        """Start the scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        logger.info("Starting scheduler...")
        
        # Task A: Price Update (every 10 seconds)
        self.scheduler.add_job(
            self._update_price_task,
            trigger=IntervalTrigger(seconds=10),
            id='price_update',
            name='Price Update Task',
            replace_existing=True
        )
        
        # Task B: Balance Sync (every 30 seconds) - KEY SOLUTION
        self.scheduler.add_job(
            self._sync_balance_task,
            trigger=IntervalTrigger(seconds=30),
            id='balance_sync',
            name='Balance Sync Task',
            replace_existing=True
        )
        
        # Task C: Cost Data Update (every 1 minute)
        self.scheduler.add_job(
            self._update_cost_task,
            trigger=IntervalTrigger(minutes=1),
            id='cost_update',
            name='Cost Data Update Task',
            replace_existing=True
        )
        
        # Task D: Health Check (every 1 minute)
        self.scheduler.add_job(
            self._health_check_task,
            trigger=IntervalTrigger(minutes=1),
            id='health_check',
            name='Health Check Task',
            replace_existing=True
        )
        
        # Task E: Data Cleanup (daily at 00:00)
        self.scheduler.add_job(
            self._cleanup_task,
            trigger=CronTrigger(hour=0, minute=0),
            id='data_cleanup',
            name='Data Cleanup Task',
            replace_existing=True
        )
        
        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started successfully with 5 tasks")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self._running:
            return
        
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown(wait=True)
        self._running = False
        logger.info("Scheduler stopped")
    
    # ===== Task Implementations =====
    
    async def _update_price_task(self):
        """Task A: Update QRL/USDT price every 10 seconds"""
        try:
            async with mexc_client:
                ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
                price = float(ticker.get("lastPrice", 0))
                volume_24h = float(ticker.get("volume", 0))
                
                # Store in Redis
                await redis_client.set_latest_price(price, volume_24h)
                await redis_client.add_price_to_history(price)
                
                logger.debug(f"[Price Update] QRL/USDT: {price:.6f}, Volume: {volume_24h:.2f}")
        
        except Exception as e:
            logger.error(f"[Price Update] Failed: {e}")
    
    async def _sync_balance_task(self):
        """Task B: Sync MEXC account balance to Redis every 30 seconds"""
        try:
            # Only run if API keys are configured
            if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
                logger.debug("[Balance Sync] Skipped - API keys not configured")
                return
            
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
                
                # Update Redis position data
                await redis_client.set_position({
                    "qrl_balance": str(qrl_balance),
                    "usdt_balance": str(usdt_balance),
                    "updated_at": datetime.now().isoformat()
                })
                
                logger.info(f"[Balance Sync] QRL: {qrl_balance:.4f}, USDT: {usdt_balance:.2f}")
        
        except Exception as e:
            logger.error(f"[Balance Sync] Failed: {e}")
    
    async def _update_cost_task(self):
        """Task C: Recalculate cost data every 1 minute"""
        try:
            position = await redis_client.get_position()
            cost_data = await redis_client.get_cost_data()
            
            qrl_balance = float(position.get("qrl_balance", 0))
            avg_cost = float(cost_data.get("avg_cost", 0))
            
            if qrl_balance > 0 and avg_cost > 0:
                # Get current price
                async with mexc_client:
                    ticker = await mexc_client.get_ticker_price("QRLUSDT")
                    current_price = float(ticker.get("price", 0))
                
                # Calculate unrealized PnL
                unrealized_pnl = (current_price - avg_cost) * qrl_balance
                total_invested = avg_cost * qrl_balance
                
                # Get existing realized PnL
                realized_pnl = float(cost_data.get("realized_pnl", 0))
                
                await redis_client.set_cost_data(
                    avg_cost=avg_cost,
                    total_invested=total_invested,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=realized_pnl
                )
                
                logger.debug(f"[Cost Update] Unrealized PnL: {unrealized_pnl:.2f} USDT")
        
        except Exception as e:
            logger.error(f"[Cost Update] Failed: {e}")
    
    async def _health_check_task(self):
        """Task D: Check system health every 1 minute"""
        try:
            health_status = {
                "redis": False,
                "mexc_api": False,
                "timestamp": datetime.now().isoformat()
            }
            
            # Check Redis
            try:
                health_status["redis"] = await redis_client.health_check()
            except Exception as e:
                logger.warning(f"[Health Check] Redis check failed: {e}")
            
            # Check MEXC API
            try:
                async with mexc_client:
                    await mexc_client.ping()
                    health_status["mexc_api"] = True
            except Exception as e:
                logger.warning(f"[Health Check] MEXC API check failed: {e}")
            
            # Log status
            if all([health_status["redis"], health_status["mexc_api"]]):
                logger.debug("[Health Check] All systems healthy")
            else:
                logger.warning(f"[Health Check] Issues detected: {health_status}")
        
        except Exception as e:
            logger.error(f"[Health Check] Failed: {e}")
    
    async def _cleanup_task(self):
        """Task E: Clean up old data daily"""
        try:
            from datetime import timedelta
            
            # Clean up price history older than 30 days
            cutoff = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
            
            # Note: Implement cleanup logic based on Redis client methods
            logger.info(f"[Data Cleanup] Cleaning data older than {cutoff}")
            
            # This would clean up old price history, trade records, etc.
            # Implementation depends on Redis client methods available
            
        except Exception as e:
            logger.error(f"[Data Cleanup] Failed: {e}")


# Global scheduler instance
trading_scheduler = TradingScheduler()
