"""
Configuration module - re-exports from legacy infrastructure.

This adapter allows src/app code to import config without depending on
root-level infrastructure directly. As legacy code is migrated, this
module will be replaced with native implementations.
"""
from infrastructure.config.config import config

__all__ = ["config"]
