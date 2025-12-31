"""
Utility functions - re-exports from legacy infrastructure.

This adapter allows src/app code to import utilities without
depending on root-level infrastructure directly.
"""
from infrastructure.utils.type_safety import safe_float

__all__ = ["safe_float"]
