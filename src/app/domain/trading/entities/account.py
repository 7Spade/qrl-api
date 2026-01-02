"""
Placeholder account domain model for progressive migration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    id: Optional[str] = None


__all__ = ["Account"]
