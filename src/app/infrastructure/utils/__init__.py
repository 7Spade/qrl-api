"""
Utility functions - native implementations.

Migrated from legacy infrastructure/utils to establish proper utilities
within the src/app structure.
"""
from .type_safety import safe_float, safe_int

__all__ = ["safe_float", "safe_int"]
