"""
Domain Exception Definitions

These exceptions represent domain-level error conditions.
They should be caught and handled at the application layer.
"""


class DomainError(Exception):
    """Base exception for all domain errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InsufficientBalanceError(DomainError):
    """Raised when account balance is insufficient for operation"""
    pass


class InvalidOrderError(DomainError):
    """Raised when an order is invalid"""
    pass


class OrderNotFoundError(DomainError):
    """Raised when an order cannot be found"""
    pass


class PositionNotFoundError(DomainError):
    """Raised when a position cannot be found"""
    pass


class RiskLimitExceededError(DomainError):
    """Raised when a risk limit is exceeded"""
    
    def __init__(self, message: str, limit_type: str, current_value: float, limit_value: float):
        super().__init__(
            message,
            {
                "limit_type": limit_type,
                "current_value": current_value,
                "limit_value": limit_value,
            }
        )


class InvalidStrategySignalError(DomainError):
    """Raised when a strategy produces an invalid signal"""
    pass


class PositionAlreadyExistsError(DomainError):
    """Raised when attempting to create a position that already exists"""
    pass


class InvalidPriceError(DomainError):
    """Raised when a price is invalid (negative, zero, etc.)"""
    pass


class InvalidQuantityError(DomainError):
    """Raised when a quantity is invalid"""
    pass


class TradingNotAllowedError(DomainError):
    """Raised when trading is not allowed (e.g., cooldown period)"""
    pass
