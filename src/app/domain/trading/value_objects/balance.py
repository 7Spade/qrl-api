"""
Placeholder balance domain model for progressive migration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Balance:
    asset: Optional[str] = None
    free: float = 0.0
    locked: float = 0.0


__all__ = ["Balance"]
