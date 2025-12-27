"""
Redis client module for managing trading bot state and data
"""
import json
import logging
from typing import Optional, Dict, Any, List
import redis
from config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for trading bot data management"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.client = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection to Redis
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                db=config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    def set_bot_status(self, status: str) -> bool:
        """
        Set bot running status
        
        Args:
            status: Bot status ('running', 'paused', 'stopped')
            
        Returns:
            bool: True if successful
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:status"
            self.client.set(key, status)
            logger.info(f"Bot status set to: {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to set bot status: {e}")
            return False
    
    def get_bot_status(self) -> Optional[str]:
        """
        Get current bot status
        
        Returns:
            str: Current status or None if not found
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:status"
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Failed to get bot status: {e}")
            return None
    
    def set_position(self, position_data: Dict[str, Any]) -> bool:
        """
        Store current position data
        
        Args:
            position_data: Dictionary containing position information
            
        Returns:
            bool: True if successful
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:position"
            self.client.set(key, json.dumps(position_data))
            logger.info(f"Position data stored: {position_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to set position: {e}")
            return False
    
    def get_position(self) -> Optional[Dict[str, Any]]:
        """
        Get current position data
        
        Returns:
            dict: Position data or None if not found
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:position"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get position: {e}")
            return None
    
    def set_latest_price(self, price: float, ttl: int = 300) -> bool:
        """
        Store latest price with TTL
        
        Args:
            price: Current price
            ttl: Time to live in seconds (default 5 minutes)
            
        Returns:
            bool: True if successful
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:price:latest"
            self.client.setex(key, ttl, str(price))
            return True
        except Exception as e:
            logger.error(f"Failed to set latest price: {e}")
            return False
    
    def get_latest_price(self) -> Optional[float]:
        """
        Get latest price
        
        Returns:
            float: Latest price or None if not found
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:price:latest"
            price = self.client.get(key)
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Failed to get latest price: {e}")
            return None
    
    def add_price_to_history(self, price: float, max_length: int = 100) -> bool:
        """
        Add price to historical data (FIFO list)
        
        Args:
            price: Price to add
            max_length: Maximum number of prices to keep
            
        Returns:
            bool: True if successful
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:price:history"
            # Add to left of list
            self.client.lpush(key, str(price))
            # Trim to max length
            self.client.ltrim(key, 0, max_length - 1)
            return True
        except Exception as e:
            logger.error(f"Failed to add price to history: {e}")
            return False
    
    def get_price_history(self, count: int = 100) -> List[float]:
        """
        Get price history
        
        Args:
            count: Number of prices to retrieve
            
        Returns:
            list: List of historical prices (most recent first)
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:price:history"
            prices = self.client.lrange(key, 0, count - 1)
            return [float(p) for p in prices]
        except Exception as e:
            logger.error(f"Failed to get price history: {e}")
            return []
    
    def increment_daily_trades(self) -> int:
        """
        Increment today's trade count
        
        Returns:
            int: Current trade count
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:trades:today"
            count = self.client.incr(key)
            # Set expiry to end of day (24 hours) if this is the first trade
            if count == 1:
                self.client.expire(key, 86400)
            return count
        except Exception as e:
            logger.error(f"Failed to increment daily trades: {e}")
            return 0
    
    def get_daily_trades(self) -> int:
        """
        Get today's trade count
        
        Returns:
            int: Number of trades today
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:trades:today"
            count = self.client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get daily trades: {e}")
            return 0
    
    def set_last_trade_time(self, timestamp: int) -> bool:
        """
        Store timestamp of last trade
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            bool: True if successful
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:last-trade"
            self.client.set(key, str(timestamp))
            return True
        except Exception as e:
            logger.error(f"Failed to set last trade time: {e}")
            return False
    
    def get_last_trade_time(self) -> Optional[int]:
        """
        Get timestamp of last trade
        
        Returns:
            int: Unix timestamp or None if not found
        """
        try:
            key = f"bot:{config.TRADING_PAIR.lower()}:last-trade"
            timestamp = self.client.get(key)
            return int(timestamp) if timestamp else None
        except Exception as e:
            logger.error(f"Failed to get last trade time: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy
        
        Returns:
            bool: True if healthy
        """
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Create singleton instance
redis_client = RedisClient()
