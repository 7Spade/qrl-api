"""
Domain Repository Interfaces

These are abstract interfaces that define contracts for data access.
Implementations live in the infrastructure layer.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class OrderRepository(ABC):
    """Repository for Order entity persistence"""
    
    @abstractmethod
    async def save(self, order) -> None:
        """Persist an order"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional:
        """Find order by ID"""
        pass
    
    @abstractmethod
    async def find_open_orders(self, symbol: str) -> List:
        """Find all open orders for a symbol"""
        pass


class PositionRepository(ABC):
    """Repository for Position entity persistence"""
    
    @abstractmethod
    async def save(self, position) -> None:
        """Persist a position"""
        pass
    
    @abstractmethod
    async def get_current(self, symbol: str) -> Optional:
        """Get current position for a symbol"""
        pass
    
    @abstractmethod
    async def get_history(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List:
        """Get position history"""
        pass


class TradeRepository(ABC):
    """Repository for Trade entity persistence"""
    
    @abstractmethod
    async def save(self, trade) -> None:
        """Persist a trade"""
        pass
    
    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List:
        """Find trades for an order"""
        pass
    
    @abstractmethod
    async def get_recent_trades(
        self, 
        symbol: str, 
        limit: int = 100
    ) -> List:
        """Get recent trades"""
        pass


class AccountRepository(ABC):
    """Repository for Account entity persistence"""
    
    @abstractmethod
    async def get_balance(self, asset: str) -> Optional:
        """Get balance for an asset"""
        pass
    
    @abstractmethod
    async def get_all_balances(self) -> List:
        """Get all account balances"""
        pass
