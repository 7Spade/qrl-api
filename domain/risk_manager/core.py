"""
Risk management domain logic (compatibility shim).

The canonical implementation now lives under `src/app/domain/risk`.
This module subclasses it to preserve existing import paths and module names
for current callers and tests.
"""

from src.app.domain.risk.limits import RiskManager as _RiskManager


class RiskManager(_RiskManager):
    """Compatibility wrapper for the migrated RiskManager."""


__all__ = ["RiskManager"]
