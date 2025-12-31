"""
Configuration module - native implementation.

Migrated from legacy infrastructure/config to establish proper config management
within the src/app structure.
"""
from .settings import Config, config

__all__ = ["Config", "config"]
