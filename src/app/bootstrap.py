"""
Placeholder bootstrap module for the future `src/app` assembly.

Current behavior is unchanged: `main.py` remains the runtime entrypoint and still
imports the legacy modules in the repository root. Use this module to wire the
interfaces, application, domain, and infrastructure packages once code is migrated,
including dependency injection, router mounting, and cross-cutting middleware.
"""


def build_app_placeholder() -> None:
    """
    Stub preserved for future wiring and DI assembly.

    Returning None makes the intent explicit that no new bootstrap logic is active yet.
    """
    return None
