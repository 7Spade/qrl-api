"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._position_updater import PositionUpdater

__all__ = ["PositionUpdater"]

