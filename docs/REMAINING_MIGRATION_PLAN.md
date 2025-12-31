# Remaining Legacy Files Migration Plan

## Current State

### Completed Migrations ✅
1. **API Layer** (26 files) → `src/app/interfaces/http/` ✓ DELETED
2. **Config** (3 files) → `src/app/infrastructure/config/` ✓ DELETED
3. **Utils** (1 file) → `src/app/infrastructure/utils/type_safety.py` ✓ DELETED
4. **Domain Interfaces** (7 files) → Already in `src/app/domain/ports/` ✓ DELETED

**Total Removed**: 37 files, 3 directories

### Remaining Legacy Files: 112

#### 1. Infrastructure (67 files)
**Location**: `infrastructure/`

**Subcategories**:
- `bot/` (10 files) - Bot runtime core, startup, execution, cleanup
- `external/mexc_client/` (17 files) - MEXC API client implementation
- `external/redis_client/` (13 files) - Redis data access layer
- `external/` (7 files) - Client facades and initialization
- `utils/` (6 files) - Metadata, keys, decorators, helpers

**Complexity**: HIGH - Deep dependencies, shared across services

#### 2. Services (18 files)
**Location**: `services/`

**Subcategories**:
- `trading/` (11 files) - Trading workflow, risk, position, strategy
- `market/` (10 files) - Price resolution, caching, market data
- `account/` (3 files) - Balance management

**Complexity**: MEDIUM - Business logic with infrastructure dependencies

#### 3. Domain (7 files)
**Location**: `domain/`

**Subcategories**:
- `risk_manager/` (2 files) - Risk calculation logic
- `position_manager/` (2 files) - Position tracking logic
- `trading_strategy/` (2 files) - Strategy implementation

**Complexity**: MEDIUM - Core domain models with service dependencies

#### 4. Repositories (13 files)
**Location**: `repositories/`

**Subcategories**:
- `trade/` (3 files) - Trade history repository
- `market/` (3 files) - Price repository
- `account/` (3 files) - Account data repository
- `position/` (2 files) - Position repository

**Complexity**: LOW - Data access patterns (depend on Redis client)

## Migration Strategy

### Phase 1: Infrastructure Utils (6 files) - LOW RISK
**Target**: `infrastructure/utils/` → `src/app/infrastructure/utils/`

**Files**:
1. `keys.py` - Redis key generators
2. `metadata.py` - Metadata helpers
3. `decorators.py` - Function decorators
4. `redis_helpers.py` - Redis utility functions
5. `__init__.py` files

**Dependencies**: Minimal - mostly pure functions

**Approach**:
1. Copy files to `src/app/infrastructure/utils/`
2. Update imports across codebase
3. Verify compilation
4. Delete legacy files

**Estimated Time**: 30 minutes

### Phase 2: Repositories (13 files) - LOW-MEDIUM RISK
**Target**: `repositories/` → `src/app/infrastructure/persistence/repos/`

**Files**:
- `market/price_repository.py` → `src/app/infrastructure/persistence/repos/price_repo.py`
- `trade/trade_repository.py` → `src/app/infrastructure/persistence/repos/trade_repo.py`
- `account/account_repository.py` → `src/app/infrastructure/persistence/repos/account_repo.py`
- `position/position_repository.py` → `src/app/infrastructure/persistence/repos/position_repo.py`

**Dependencies**: Redis client only

**Approach**:
1. Create target directory structure
2. Migrate repository implementations
3. Update all service imports
4. Verify data access works
5. Delete legacy repository files

**Estimated Time**: 1.5 hours

### Phase 3: Domain Models (7 files) - MEDIUM RISK
**Target**: `domain/` → `src/app/domain/`

**Files**:
- `risk_manager/core.py` → `src/app/domain/risk/manager.py`
- `position_manager/core.py` → `src/app/domain/position/manager.py`
- `trading_strategy/core.py` → `src/app/domain/strategies/trading_strategy.py`

**Dependencies**: Config, repositories, some services

**Approach**:
1. Analyze domain dependencies
2. Migrate domain models to `src/app/domain/`
3. Update service layer imports
4. Verify business logic unchanged
5. Delete legacy domain files

**Estimated Time**: 2 hours

### Phase 4: Redis Client (13 files) - HIGH RISK
**Target**: `infrastructure/external/redis_client/` → `src/app/infrastructure/persistence/redis/`

**Files**:
- `core.py` → `src/app/infrastructure/persistence/redis/client.py`
- `*_repo.py` files → `src/app/infrastructure/persistence/redis/repos/`
- `*_cache.py` files → `src/app/infrastructure/persistence/redis/cache/`

**Dependencies**: Config, widely used across services

**Approach**:
1. Create Redis infrastructure in new location
2. Migrate client core
3. Migrate repos and caches
4. Update all imports (services, repositories, domain)
5. Extensive testing
6. Delete legacy Redis files

**Estimated Time**: 3 hours

### Phase 5: MEXC Client (17 files) - HIGH RISK
**Target**: `infrastructure/external/mexc_client/` → `src/app/infrastructure/exchange/mexc/`

**Files**:
- `client.py` → `src/app/infrastructure/exchange/mexc/client.py`
- `account.py`, `market.py`, `trading.py` → respective modules
- `signer.py`, `config.py` → supporting files

**Dependencies**: Config, used by all services

**Approach**:
1. Create MEXC infrastructure in new location
2. Migrate client implementation
3. Migrate API modules (market, account, trading)
4. Update all service imports
5. Test all API endpoints
6. Delete legacy MEXC files

**Estimated Time**: 3 hours

### Phase 6: Bot Runtime (10 files) - HIGH RISK
**Target**: `infrastructure/bot/` → `src/app/infrastructure/bot_runtime/`

**Files**:
- `bot_core/core.py` → `src/app/infrastructure/bot_runtime/core.py`
- `bot_core/startup.py`, `cleanup.py` → lifecycle modules
- `bot_core/execution.py`, `strategy.py` → execution modules
- `bot_utils.py` → utilities

**Dependencies**: Services, domain, Redis, MEXC

**Approach**:
1. Create bot runtime infrastructure
2. Migrate bot core modules
3. Update main.py and bot endpoints
4. Test bot start/stop lifecycle
5. Delete legacy bot files

**Estimated Time**: 2 hours

### Phase 7: Services Layer (18 files) - MEDIUM-HIGH RISK
**Target**: `services/` → `src/app/application/`

**Files**:
- `trading/*` → `src/app/application/trading/`
- `market/*` → `src/app/application/market/`
- `account/*` → `src/app/application/account/`

**Dependencies**: All infrastructure, domain, repositories

**Approach**:
1. Migrate trading services (already partially done)
2. Migrate market services
3. Migrate account services
4. Update all imports in interfaces and domain
5. Verify all business logic works
6. Delete legacy service files

**Estimated Time**: 3 hours

## Dependency Order (Bottom-Up)

```
1. Utils (no deps) ← START HERE
2. Redis Client (uses utils)
3. MEXC Client (uses utils, config)
4. Repositories (use Redis client)
5. Domain Models (use repositories, config)
6. Services (use domain, repositories, clients)
7. Bot Runtime (uses everything) ← END HERE
```

## Risk Mitigation

### Critical Success Factors
1. **One phase at a time** - Complete and verify before moving to next
2. **Import updates must be complete** - Use grep to find all references
3. **Test after each phase** - Verify endpoints and bot still work
4. **Keep backups** - Git commit after each successful phase

### Testing Checklist Per Phase
- [ ] All files compile without import errors
- [ ] API endpoints respond correctly
- [ ] Bot can start and stop
- [ ] Balance and price data accessible
- [ ] Trading workflow executes
- [ ] No remaining imports from legacy paths

### Rollback Strategy
Each phase is a separate commit. If issues arise:
1. Identify the failing commit
2. `git revert <commit-hash>`
3. Investigate and fix
4. Re-attempt migration

## File Size Constraint

All migrated files must stay under 4000 characters. If a file exceeds this:
- Split into multiple modules
- Extract helper functions
- Create submodules

## Execution Plan

### Week 1
- **Day 1**: Phases 1-2 (Utils + Repositories) - 2 hours
- **Day 2**: Phase 3 (Domain Models) - 2 hours
- **Day 3**: Phase 4 (Redis Client) - 3 hours
- **Day 4**: Phase 5 (MEXC Client) - 3 hours

### Week 2
- **Day 5**: Phase 6 (Bot Runtime) - 2 hours
- **Day 6**: Phase 7 (Services) - 3 hours
- **Day 7**: Final verification and cleanup - 2 hours

**Total Estimated Time**: 17 hours over 7 days

## Success Criteria

✅ All 112 legacy files migrated to `src/app/`
✅ Zero imports from `infrastructure/`, `services/`, `domain/`, `repositories/`
✅ All API endpoints functional
✅ Bot runtime operational
✅ All tests passing
✅ Legacy directories deleted

## Next Immediate Action

Start with **Phase 1: Infrastructure Utils** as it has no dependencies and is the safest migration to begin with.
