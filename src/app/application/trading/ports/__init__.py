"""
Application Trading Ports (Outbound Interfaces)

This module contains port interfaces (outbound dependencies) for the application layer.
In Clean Architecture, ports define interfaces that infrastructure adapters must implement.

Ports are the Dependency Inversion Principle in action:
- High-level application logic depends on abstractions (ports)
- Low-level infrastructure implements these abstractions
- Direction of dependency: Infrastructure → Application → Domain

Port Types:
- Market Ports: Access to market data providers
- Execution Ports: Order placement and management
- Account Ports: Account and balance information
- Position Ports: Position tracking and management
- Price/Cost Ports: Pricing and cost calculation
"""

from src.app.application.trading.ports.account_port import *
from src.app.application.trading.ports.cost_port import *
from src.app.application.trading.ports.execution_port import *
from src.app.application.trading.ports.market_feed import *
from src.app.application.trading.ports.market_port import *
from src.app.application.trading.ports.position_port import *
from src.app.application.trading.ports.price_port import *
from src.app.application.trading.ports.trade_port import *

__all__ = [
    # Market data ports
    "IMarketDataProvider",
    "MarketFeedPort",
    "MarketPort",
    
    # Trading ports
    "ExecutionPort",
    "TradePort",
    
    # Account & Position ports
    "AccountPort",
    "PositionPort",
    
    # Pricing ports
    "PricePort",
    "CostPort",
]
