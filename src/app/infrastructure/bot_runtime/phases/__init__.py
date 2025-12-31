"""Bot execution phases."""
from src.app.infrastructure.bot_runtime.phases.startup import phase_startup
from src.app.infrastructure.bot_runtime.phases.data_collection import phase_data_collection
from src.app.infrastructure.bot_runtime.phases.strategy import phase_strategy
from src.app.infrastructure.bot_runtime.phases.risk import phase_risk_control
from src.app.infrastructure.bot_runtime.phases.execution import phase_execution
from src.app.infrastructure.bot_runtime.phases.cleanup import phase_cleanup

__all__ = [
    "phase_startup",
    "phase_data_collection",
    "phase_strategy",
    "phase_risk_control",
    "phase_execution",
    "phase_cleanup",
]
