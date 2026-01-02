"""Application Use Cases

Use cases represent application-specific business rules and orchestrate domain logic.
They are the entry points for features from the interface layer.

Current use cases (organized by domain):
- Trading workflow: execute_trade, manage_risk, validate_trade, update_position, trading_workflow
- Account data: get_orders, get_trades  
- Market data: get_klines, get_orderbook, get_price

Note: Many of these are currently shims for backward compatibility.
Future refactoring will transform them into proper use case implementations with:
- Constructor injection of ports
- Clear single responsibility  
- Orchestration without business logic
"""

# Trading workflow use cases
from .execute_trade_use_case import *
from .manage_risk_use_case import *
from .update_position_use_case import *
from .validate_trade_use_case import *
from .trading_workflow import *

# Account data use cases
from .get_orders_use_case import *
from .get_trades_use_case import *

# Market data use cases
from .get_klines_use_case import *
from .get_orderbook_use_case import *
from .get_price_use_case import *
