# QRL Trading API Architecture Restructuring Plan

## Executive Summary

This document outlines a comprehensive plan to restructure the QRL Trading API codebase to fully comply with the Clean Architecture principles defined in `docs/✨.md`. The restructuring will maintain all existing functionality while organizing code according to proper layered architecture patterns.

## Current Architecture State

### Directory Structure Overview

```
src/app/
├── domain/              # ⚠️ Needs reorganization
│   ├── events/
│   ├── models/          # Should split into entities/ and value_objects/
│   ├── ports/           # ❌ Should be in application layer
│   ├── position/
│   ├── risk/
│   └── strategies/
├── application/         # ⚠️ Needs consolidation
│   ├── account/
│   ├── bot/
│   ├── market/
│   └── trading/        # Partially correct structure
├── infrastructure/      # ⚠️ Has duplication
│   ├── external/
│   │   └── mexc/       # ❌ Duplicate of exchange/mexc
│   ├── exchange/
│   │   └── mexc/
│   ├── bot_runtime/
│   ├── redis/
│   ├── scheduler/
│   └── utils/
├── interfaces/          # ⚠️ Missing some required dirs
│   ├── http/
│   ├── tasks/          # Should rename to background/
│   └── templates/
└── shared/             # ✅ Correct
```

### Target Architecture (from ✨.md)

```
src/app/
├── domain/                # 🔴 Pure business logic
│   └── trading/
│       ├── entities/
│       ├── value_objects/
│       ├── strategies/
│       ├── services/
│       ├── events/
│       ├── repositories.py    # interfaces only
│       └── errors.py
├── application/           # 🟠 Use case orchestration
│   └── trading/
│       ├── use_cases/
│       ├── services/
│       ├── ports/            # outbound ports
│       ├── dtos/
│       └── commands/
├── infrastructure/        # 🟡 Technical implementation
│   ├── exchange/
│   │   └── mexc/
│   │       ├── rest_client.py
│   │       ├── ws_client.py
│   │       ├── signer.py
│   │       ├── adapters.py
│   │       └── protobuf_decoder.py
│   ├── redis/
│   ├── supabase/
│   └── scheduler/
├── interfaces/            # 🟢 I/O layer
│   ├── http/
│   │   ├── routes/
│   │   ├── schemas.py
│   │   └── deps.py
│   ├── websocket/
│   ├── background/
│   └── cli/
└── shared/                # ⚪ Cross-layer utilities
```

## Gap Analysis

### Domain Layer Gaps

| Current | Required | Action |
|---------|----------|--------|
| domain/models/ | domain/trading/entities/ | Move & rename |
| domain/models/ | domain/trading/value_objects/ | Extract value objects |
| domain/strategies/ | domain/trading/strategies/ | Move |
| domain/events/ | domain/trading/events/ | Move |
| domain/position/ | domain/trading/services/ | Move & refactor |
| domain/risk/ | domain/trading/services/ | Move & refactor |
| domain/ports/ | ❌ Move to application | Move to application |
| ❌ Missing | domain/trading/repositories.py | Create abstractions |
| ❌ Missing | domain/trading/errors.py | Create domain exceptions |

### Application Layer Gaps

| Current | Required | Action |
|---------|----------|--------|
| application/account/ | application/trading/use_cases/ | Consolidate |
| application/bot/ | application/trading/services/ | Consolidate |
| application/market/ | application/trading/use_cases/ | Consolidate |
| application/trading/ | application/trading/ | Reorganize |
| domain/ports/ | application/trading/ports/ | Move from domain |
| ❌ Missing | application/trading/dtos/ | Extract from services |
| ❌ Missing | application/trading/commands/ | Create command objects |

### Infrastructure Layer Gaps

| Current | Required | Action |
|---------|----------|--------|
| infrastructure/external/mexc/ | ❌ Remove | Consolidate |
| infrastructure/exchange/mexc/ | ✅ Keep & enhance | Refactor |
| infrastructure/redis/ | ✅ Keep | Verify structure |
| infrastructure/scheduler/ | ✅ Keep | Verify structure |

### Interfaces Layer Gaps

| Current | Required | Action |
|---------|----------|--------|
| interfaces/http/ | ✅ Keep | Verify routes/ structure |
| interfaces/tasks/ | interfaces/background/ | Rename |
| ❌ Missing | interfaces/websocket/ | Create if needed |
| ❌ Missing | interfaces/cli/ | Create if needed |

## Detailed Restructuring Plan

### Phase 1: Domain Layer Reorganization

**Complexity**: 7/10  
**Duration**: 2-3 days  
**Risk**: Medium

#### Tasks

1. **Create domain/trading/ structure**
   ```bash
   mkdir -p src/app/domain/trading/{entities,value_objects,strategies,services,events}
   touch src/app/domain/trading/{repositories.py,errors.py,__init__.py}
   ```

2. **Migrate entities**
   - Move `domain/models/order.py` → `domain/trading/entities/order.py`
   - Move `domain/models/trade.py` → `domain/trading/entities/trade.py`
   - Move `domain/models/position.py` → `domain/trading/entities/position.py`
   - Move `domain/models/account.py` → `domain/trading/entities/account.py`

3. **Extract value objects**
   - Move `domain/models/price.py` → `domain/trading/value_objects/price.py`
   - Move `domain/models/balance.py` → `domain/trading/value_objects/balance.py`
   - Create `domain/trading/value_objects/symbol.py` (if needed)
   - Create `domain/trading/value_objects/quantity.py` (if needed)

4. **Migrate strategies**
   - Move `domain/strategies/*` → `domain/trading/strategies/`
   - Maintain `base.py`, `indicators/`, `filters/` structure

5. **Migrate events**
   - Move `domain/events/*` → `domain/trading/events/`

6. **Migrate services**
   - Move `domain/position/calculator.py` → `domain/trading/services/position_calculator.py`
   - Move `domain/position/updater.py` → `domain/trading/services/position_updater.py`
   - Move `domain/risk/*` → `domain/trading/services/risk/`

7. **Create repository abstractions**
   ```python
   # domain/trading/repositories.py
   from abc import ABC, abstractmethod
   from typing import Optional, List
   
   class OrderRepository(ABC):
       @abstractmethod
       async def save(self, order): ...
       
       @abstractmethod
       async def find_by_id(self, order_id: str) -> Optional: ...
   
   class PositionRepository(ABC):
       @abstractmethod
       async def save(self, position): ...
       
       @abstractmethod
       async def get_current(self, symbol: str) -> Optional: ...
   ```

8. **Create domain exceptions**
   ```python
   # domain/trading/errors.py
   class DomainError(Exception):
       """Base domain exception"""
   
   class InsufficientBalanceError(DomainError):
       """Raised when balance is insufficient for operation"""
   
   class InvalidOrderError(DomainError):
       """Raised when order is invalid"""
   
   class RiskLimitExceededError(DomainError):
       """Raised when risk limits are exceeded"""
   ```

9. **Update imports**
   - Update all files importing from old locations
   - Run tests to verify no breakage

10. **Clean up old structure**
    - Remove `domain/models/`
    - Remove `domain/position/`
    - Remove `domain/risk/`
    - Remove `domain/strategies/`
    - Remove `domain/events/`

### Phase 2: Application Layer Reorganization

**Complexity**: 8/10  
**Duration**: 3-4 days  
**Risk**: High

#### Tasks

1. **Create application/trading/ structure**
   ```bash
   mkdir -p src/app/application/trading/{use_cases,services,ports,dtos,commands}
   ```

2. **Define ports (move from domain)**
   - Move `domain/ports/*` → `application/trading/ports/`
   - Refactor as outbound port interfaces

3. **Create DTOs**
   - Extract DTOs from existing services
   - Create `application/trading/dtos/signal_dto.py`
   - Create `application/trading/dtos/order_dto.py`
   - Create `application/trading/dtos/position_dto.py`

4. **Create commands**
   ```python
   # application/trading/commands/place_order_command.py
   from dataclasses import dataclass
   
   @dataclass
   class PlaceOrderCommand:
       symbol: str
       side: str
       quantity: float
       price: Optional[float] = None
   ```

5. **Organize use cases**
   - Move `application/market/get_*.py` → `application/trading/use_cases/`
   - Move `application/account/get_*.py` → `application/trading/use_cases/`
   - Move `application/trading/execute_trade.py` → `application/trading/use_cases/`

6. **Organize services**
   - Consolidate `application/bot/` → `application/trading/services/bot/`
   - Keep existing `application/trading/services/` structure
   - Add orchestration services as needed

7. **Update imports**
   - Update all imports from old application structure
   - Update dependency injection

8. **Clean up old structure**
   - Remove `application/account/`
   - Remove `application/bot/`
   - Remove `application/market/`

### Phase 3: Infrastructure Consolidation

**Complexity**: 6/10  
**Duration**: 1-2 days  
**Risk**: Medium

#### Tasks

1. **Analyze MEXC implementations**
   - Compare `infrastructure/external/mexc/` vs `infrastructure/exchange/mexc/`
   - Identify overlaps and differences

2. **Consolidate to infrastructure/exchange/mexc/**
   - Keep the better implementation
   - Merge unique functionality
   - Ensure proper structure:
     - `rest_client.py` - HTTP client
     - `ws_client.py` - WebSocket client
     - `signer.py` - HMAC signature
     - `adapters.py` - Port implementations
     - `protobuf_decoder.py` - Protocol buffer handling

3. **Update imports**
   - Update all references to old MEXC location
   - Update dependency injection configuration

4. **Verify other infrastructure**
   - Check `infrastructure/redis/` structure
   - Check `infrastructure/scheduler/` structure
   - Clean up `infrastructure/utils/` if needed

5. **Remove duplicates**
   - Delete `infrastructure/external/mexc/`
   - Delete `infrastructure/external/` if empty

### Phase 4: Interfaces Layer Updates

**Complexity**: 5/10  
**Duration**: 1 day  
**Risk**: Low

#### Tasks

1. **Verify HTTP structure**
   - Ensure `interfaces/http/routes/` exists
   - Ensure proper route organization
   - Create `interfaces/http/schemas.py` if missing
   - Create `interfaces/http/deps.py` if missing

2. **Rename tasks to background**
   - Rename `interfaces/tasks/` → `interfaces/background/`
   - Update imports

3. **Create WebSocket directory (if needed)**
   - Check if WebSocket endpoints exist
   - Create `interfaces/websocket/` structure
   - Move WebSocket handlers

4. **Create CLI directory (if needed)**
   - Check if CLI commands exist
   - Create `interfaces/cli/` structure
   - Move CLI handlers

### Phase 5: Import Updates & Testing

**Complexity**: 9/10  
**Duration**: 2-3 days  
**Risk**: High

#### Tasks

1. **Update all imports systematically**
   - Use find/replace for common patterns
   - Update one layer at a time
   - Test after each layer update

2. **Update dependency injection**
   - Update `bootstrap.py`
   - Update FastAPI dependencies
   - Update test fixtures

3. **Update tests**
   - Update test imports
   - Update mock structures
   - Ensure all tests pass

4. **Update main application**
   - Update `main.py` imports
   - Update router registration
   - Test application startup

5. **Run full test suite**
   - Unit tests
   - Integration tests
   - End-to-end tests

6. **Manual testing**
   - Test all API endpoints
   - Test WebSocket connections
   - Test background tasks
   - Test CLI commands (if any)

### Phase 6: Documentation & Validation

**Complexity**: 4/10  
**Duration**: 1 day  
**Risk**: Low

#### Tasks

1. **Update README.md**
   - Update project structure documentation
   - Update development guide
   - Add architecture diagram

2. **Create architecture documentation**
   - Document layer responsibilities
   - Document dependencies
   - Create package diagram

3. **Run architecture validation**
   - Use `architecture_guard.py` to validate
   - Fix any violations
   - Document exceptions (if any)

4. **Update CHANGELOG**
   - Document structural changes
   - Note any breaking changes
   - Reference this plan

## Risk Management

### High-Risk Areas

1. **Import dependencies** - Most critical, affects entire codebase
2. **Application layer** - Complex interdependencies
3. **Testing infrastructure** - May need significant updates

### Mitigation Strategies

1. **Work in feature branch** - Easy rollback if needed
2. **Incremental changes** - One phase at a time
3. **Continuous testing** - Run tests after each change
4. **Pair programming** - Complex refactoring needs review
5. **Documentation** - Document decisions and changes

### Rollback Plan

If critical issues arise:
1. Revert to main branch
2. Analyze failure points
3. Create smaller, safer refactoring plan
4. Re-attempt with adjusted approach

## Success Criteria

### Functional Requirements
- [ ] All tests passing
- [ ] All API endpoints functional
- [ ] WebSocket connections working
- [ ] Background tasks executing
- [ ] No runtime errors

### Structural Requirements
- [ ] Domain layer follows ✨.md structure exactly
- [ ] Application layer follows ✨.md structure exactly
- [ ] Infrastructure layer follows ✨.md structure exactly
- [ ] Interfaces layer follows ✨.md structure exactly
- [ ] No architecture violations detected

### Quality Requirements
- [ ] Test coverage maintained or improved
- [ ] Code quality scores maintained
- [ ] Performance not degraded
- [ ] Documentation complete and accurate

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 2-3 days | None |
| Phase 2 | 3-4 days | Phase 1 |
| Phase 3 | 1-2 days | None (parallel to Phase 2) |
| Phase 4 | 1 day | None (parallel to Phase 2) |
| Phase 5 | 2-3 days | Phases 1, 2, 3, 4 |
| Phase 6 | 1 day | Phase 5 |
| **Total** | **10-14 days** | Sequential + parallel work |

## Next Steps

1. Review and approve this plan
2. Create feature branch: `feature/architecture-restructure`
3. Begin Phase 1 execution
4. Regular check-ins and progress reports
5. Final review and merge to main

## References

- [✨.md](./✨.md) - Clean Architecture guide
- [ARCHITECTURE_ALIGNMENT.md](./ARCHITECTURE_ALIGNMENT.md) - Current alignment doc (if exists)
- [architecture_guard.py](../architecture_guard.py) - Architecture validation tool
