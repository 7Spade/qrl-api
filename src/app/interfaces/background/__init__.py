"""Background Task Interface Layer

External entry points for Cloud Scheduler and other background task systems.
These are analogous to interfaces/http/ for REST endpoints.

Task handlers:
- task_sync_balance: Scheduled balance synchronization
- task_update_cost: Scheduled cost data updates
- task_update_price: Scheduled price data updates

Clean Architecture: These are adapters in the interfaces layer that call
application use cases or services. They handle external trigger mechanisms
(Cloud Scheduler auth, request parsing) and delegate to application layer.
"""

from .task_sync_balance import task_sync_balance
from .task_update_cost import task_update_cost
from .task_update_price import task_update_price

__all__ = [
    "task_sync_balance",
    "task_update_cost",
    "task_update_price",
]
