"""Legacy shim - redirects to src.app.application.trading"""
from src.app.application.trading._risk_service import RiskService

__all__ = ["RiskService"]

