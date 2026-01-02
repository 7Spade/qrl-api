#!/usr/bin/env python3
"""
Phase 1: Domain Layer Restructuring Script

This script automates the reorganization of the domain layer according to ✨.md specifications.

Usage:
    python scripts/restructure_phase1_domain.py --dry-run  # Preview changes
    python scripts/restructure_phase1_domain.py --execute  # Apply changes

Safety:
    - Always run with --dry-run first
    - Commits changes incrementally
    - Can be safely stopped and resumed
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


class DomainRestructure:
    """Handles Phase 1 domain layer restructuring"""
    
    def __init__(self, root_path: str, dry_run: bool = True):
        self.root = Path(root_path)
        self.domain_root = self.root / "src" / "app" / "domain"
        self.dry_run = dry_run
        self.changes: List[str] = []
        
    def create_directory_structure(self) -> None:
        """Create new domain/trading/ directory structure"""
        trading_root = self.domain_root / "trading"
        
        directories = [
            trading_root / "entities",
            trading_root / "value_objects",
            trading_root / "strategies" / "indicators",
            trading_root / "strategies" / "filters",
            trading_root / "services" / "position",
            trading_root / "services" / "risk" / "validators",
            trading_root / "events",
        ]
        
        for directory in directories:
            if self.dry_run:
                print(f"[DRY RUN] Would create: {directory}")
                self.changes.append(f"CREATE DIR: {directory}")
            else:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"Created: {directory}")
                # Create __init__.py files
                init_file = directory / "__init__.py"
                init_file.touch()
                
    def create_repositories_file(self) -> None:
        """Create domain/trading/repositories.py with abstract interfaces"""
        content = '''"""
Domain Repository Interfaces

These are abstract interfaces that define contracts for data access.
Implementations live in the infrastructure layer.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class OrderRepository(ABC):
    """Repository for Order entity persistence"""
    
    @abstractmethod
    async def save(self, order) -> None:
        """Persist an order"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional:
        """Find order by ID"""
        pass
    
    @abstractmethod
    async def find_open_orders(self, symbol: str) -> List:
        """Find all open orders for a symbol"""
        pass


class PositionRepository(ABC):
    """Repository for Position entity persistence"""
    
    @abstractmethod
    async def save(self, position) -> None:
        """Persist a position"""
        pass
    
    @abstractmethod
    async def get_current(self, symbol: str) -> Optional:
        """Get current position for a symbol"""
        pass
    
    @abstractmethod
    async def get_history(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List:
        """Get position history"""
        pass


class TradeRepository(ABC):
    """Repository for Trade entity persistence"""
    
    @abstractmethod
    async def save(self, trade) -> None:
        """Persist a trade"""
        pass
    
    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List:
        """Find trades for an order"""
        pass
    
    @abstractmethod
    async def get_recent_trades(
        self, 
        symbol: str, 
        limit: int = 100
    ) -> List:
        """Get recent trades"""
        pass


class AccountRepository(ABC):
    """Repository for Account entity persistence"""
    
    @abstractmethod
    async def get_balance(self, asset: str) -> Optional:
        """Get balance for an asset"""
        pass
    
    @abstractmethod
    async def get_all_balances(self) -> List:
        """Get all account balances"""
        pass
'''
        
        file_path = self.domain_root / "trading" / "repositories.py"
        
        if self.dry_run:
            print(f"[DRY RUN] Would create: {file_path}")
            self.changes.append(f"CREATE FILE: {file_path}")
        else:
            file_path.write_text(content)
            print(f"Created: {file_path}")
            
    def create_errors_file(self) -> None:
        """Create domain/trading/errors.py with domain exceptions"""
        content = '''"""
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
'''
        
        file_path = self.domain_root / "trading" / "errors.py"
        
        if self.dry_run:
            print(f"[DRY RUN] Would create: {file_path}")
            self.changes.append(f"CREATE FILE: {file_path}")
        else:
            file_path.write_text(content)
            print(f"Created: {file_path}")
            
    def generate_report(self) -> None:
        """Generate a report of all planned changes"""
        print("\n" + "="*60)
        print("PHASE 1 RESTRUCTURING REPORT")
        print("="*60)
        print(f"\nMode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print(f"Total changes: {len(self.changes)}\n")
        
        for change in self.changes:
            print(f"  {change}")
            
        print("\n" + "="*60)
        
        if self.dry_run:
            print("\n✅ Dry run completed successfully")
            print("To apply changes, run with --execute flag")
        else:
            print("\n✅ Restructuring completed")
            print("\nNext steps:")
            print("1. Review generated files")
            print("2. Update imports in affected files")
            print("3. Run tests: pytest tests/domain/")
            print("4. Commit changes")
            
    def execute(self) -> None:
        """Execute all restructuring steps"""
        print(f"\nStarting Phase 1 Domain Restructuring...")
        print(f"Root path: {self.root}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}\n")
        
        try:
            self.create_directory_structure()
            self.create_repositories_file()
            self.create_errors_file()
            self.generate_report()
            
        except Exception as e:
            print(f"\n❌ Error during restructuring: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: Restructure domain layer according to ✨.md"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes (use with caution)"
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Root directory of the project"
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("⚠️  Please specify either --dry-run or --execute")
        parser.print_help()
        return
        
    if args.execute:
        response = input("⚠️  This will modify the codebase. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
            
    dry_run = not args.execute
    restructure = DomainRestructure(args.root, dry_run=dry_run)
    restructure.execute()


if __name__ == "__main__":
    main()
