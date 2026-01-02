"""
Domain Models Package (Legacy Compatibility)

⚠️ DEPRECATED: This module provides backward compatibility only.

New code should use:
    from src.app.domain.trading.entities import Order, Account, Position, Trade
    from src.app.domain.trading.value_objects import Balance, Price

This backward compatibility layer will be maintained for at least 2 major versions
to allow gradual migration. See docs/PHASE1_STAGES_5_6_COMPLETION.md for migration guide.
"""

import warnings

warnings.warn(
    "domain.models is deprecated. Use domain.trading.entities and domain.trading.value_objects instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.app.domain.trading.entities.account import Account
from src.app.domain.trading.entities.order import Order
from src.app.domain.trading.entities.position import Position
from src.app.domain.trading.entities.trade import Trade
from src.app.domain.trading.value_objects.balance import Balance
from src.app.domain.trading.value_objects.price import Price

__all__ = [
    "Account",
    "Balance",
    "Order",
    "Position",
    "Price",
    "Trade",
]

