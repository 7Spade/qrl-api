"""
Signature helper shim.

Delegates to the legacy signature generator to avoid behavior changes.
"""

from src.app.infrastructure.external.mexc.signer import generate_signature

__all__ = ["generate_signature"]
