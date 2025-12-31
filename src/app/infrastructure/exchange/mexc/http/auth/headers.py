"""
Header builder shim for authenticated MEXC requests.
"""
from typing import Dict

from src.app.infrastructure.external.mexc.config import load_settings


def build_headers() -> Dict[str, str]:
    """Return default headers matching the legacy client configuration."""
    settings = load_settings()
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if settings.api_key:
        headers["X-MEXC-APIKEY"] = settings.api_key
    return headers


__all__ = ["build_headers"]
