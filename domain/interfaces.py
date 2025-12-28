"""
Domain interfaces for dependency inversion
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IMarketDataProvider(ABC):
    """Interface for market data access"""
    
    @abstractmethod
    async def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """Get 24-hour ticker data"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        pass
    
    @abstractmethod
    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price"""
        pass


class IAccountDataProvider(ABC):
    """Interface for account data access"""
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        pass
    
    @abstractmethod
    async def create_order(self, symbol: str, side: str, order_type: str, **kwargs) -> Dict[str, Any]:
        """Create a trading order"""
        pass


class IPositionRepository(ABC):
    """Interface for position data storage"""
    
    @abstractmethod
    async def get_position(self) -> Dict[str, str]:
        """Get current position data"""
        pass
    
    @abstractmethod
    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        """Update position data"""
        pass
    
    @abstractmethod
    async def get_position_layers(self) -> Dict[str, str]:
        """Get position layer configuration"""
        pass


class IPriceRepository(ABC):
    """Interface for price data storage"""
    
    @abstractmethod
    async def get_latest_price(self) -> Optional[Dict[str, str]]:
        """Get latest price data"""
        pass
    
    @abstractmethod
    async def set_latest_price(self, price: float, volume: float) -> bool:
        """Store latest price"""
        pass
    
    @abstractmethod
    async def get_price_history(self, limit: int) -> List[float]:
        """Get price history"""
        pass


class ITradeRepository(ABC):
    """Interface for trade history storage"""
    
    @abstractmethod
    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        """Add trade to history"""
        pass
    
    @abstractmethod
    async def get_trade_history(self, limit: int) -> List[Dict[str, Any]]:
        """Get trade history"""
        pass
    
    @abstractmethod
    async def get_daily_trades(self) -> int:
        """Get count of trades today"""
        pass
    
    @abstractmethod
    async def increment_daily_trades(self) -> bool:
        """Increment daily trade counter"""
        pass
    
    @abstractmethod
    async def get_last_trade_time(self) -> Optional[int]:
        """Get timestamp of last trade"""
        pass
    
    @abstractmethod
    async def set_last_trade_time(self) -> bool:
        """Update last trade timestamp"""
        pass


class ICostRepository(ABC):
    """Interface for cost tracking storage"""
    
    @abstractmethod
    async def get_cost_data(self) -> Dict[str, str]:
        """Get cost tracking data"""
        pass
    
    @abstractmethod
    async def set_cost_data(self, avg_cost: float, total_invested: float, 
                           unrealized_pnl: float = 0, realized_pnl: float = 0) -> bool:
        """Update cost tracking data"""
        pass
