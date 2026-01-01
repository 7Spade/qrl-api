"""
Interfaces layer - HTTP and Task endpoints.

This module exports the centralized router registry for simplified
application setup.
"""

from src.app.interfaces.router_registry import register_all_routers

__all__ = ["register_all_routers"]
