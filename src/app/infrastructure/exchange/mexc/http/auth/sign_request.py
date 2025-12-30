"""
Signature helper shim.

Delegates to the legacy signature generator to avoid behavior changes.
"""

from infrastructure.external.mexc_client.signer import generate_signature

__all__ = ["generate_signature"]
