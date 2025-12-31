# Complete Migration Plan: Legacy to src/app Architecture

## Executive Summary

**Current Status**: ~40% complete (repositories + core trading services migrated)
**Remaining Files**: 142 legacy Python files across 4 directories
**Estimated Time**: 1.5-2 work days for complete migration
**Approach**: Phased migration with backward-compatible shims, no breaking changes

---

## Phase Breakdown

### ✅ Phase 1: Repositories (COMPLETE)
- **Status**: 100% complete
- **Files**: 5 repository classes migrated
- **Location**: `src/app/infrastructure/persistence/redis/repos/`
- **Shims**: Created in `/repositories/__init__.py`

### ✅ Phase 2: Trading Services (COMPLETE)
- **Status**: 85% complete (6/7 files migrated)
- **Files**: Helper services migrated, core service updated
- **Location**: `src/app/application/trading/`
- **Remaining**: `trading_service_core.py` (11939 bytes, needs splitting)

### 🔄 Phase 3: Domain Layer (NEXT - 0.5 days)
- **Status**: 0% complete
- **Files**: 14 Python files in `/domain/`
- **Target**: `src/app/domain/`
- **Priority**: HIGH (dependencies for other layers)

### 🔄 Phase 4: Infrastructure Layer (0.75 days)
- **Status**: 10% complete (config + skeleton created)
- **Files**: 71 Python files in `/infrastructure/`
- **Target**: `src/app/infrastructure/`
- **Priority**: HIGH (MEXC + Redis clients needed)

### 🔄 Phase 5: Services Completion (0.25 days)
- **Status**: 30% complete (trading done, others pending)
- **Files**: 25 Python files in `/services/`
- **Target**: Various locations in `src/app/application/`
- **Priority**: MEDIUM

### 🔄 Phase 6: API Layer (0.5 days)
- **Status**: 20% complete (HTTP shims created)
- **Files**: 32 Python files in `/api/`
- **Target**: `src/app/interfaces/http/`
- **Priority**: MEDIUM

### 🔄 Phase 7: Legacy Cleanup (0.25 days)
- **Status**: Not started
- **Action**: Remove legacy directories after verification
- **Priority**: LOW (final step)

---

## Detailed Task List

### Phase 3: Domain Layer Migration (Day 1: Morning)

#### Task 3.1: Domain Interfaces → Ports (1 hour)
**Files to migrate** (7 files):
```
domain/interfaces/cost.py → src/app/domain/ports/cost_port.py
domain/interfaces/market.py → src/app/domain/ports/market_port.py
domain/interfaces/trade.py → src/app/domain/ports/trade_port.py
domain/interfaces/position.py → src/app/domain/ports/position_port.py
domain/interfaces/account.py → src/app/domain/ports/account_port.py
domain/interfaces/price.py → src/app/domain/ports/price_port.py
```

**Actions**:
1. Read each interface file
2. Convert to Protocol/ABC if not already
3. Create in `src/app/domain/ports/`
4. Update imports in existing src/app files
5. Create shim in `domain/interfaces/__init__.py`

**Verification**:
- Check all files are <4000 bytes
- Ensure Protocol/ABC inheritance correct
- Test imports work from src/app

#### Task 3.2: Risk Manager → Domain Risk (45 min)
**Files to migrate** (2 files):
```
domain/risk_manager/core.py → src/app/domain/risk/*.py
domain/risk_manager/__init__.py → update shim
```

**Actions**:
1. Analyze `risk_manager/core.py` structure
2. Split if >4000 bytes into logical units
3. Map to existing `src/app/domain/risk/` (limits.py, stop_loss.py)
4. Merge or extend existing files
5. Create compatibility shim

**Verification**:
- Risk logic behavior unchanged
- All risk checks still work
- Test with existing trading workflow

#### Task 3.3: Trading Strategy → Domain Strategies (45 min)
**Files to migrate** (2 files):
```
domain/trading_strategy/core.py → src/app/domain/strategies/*.py
domain/trading_strategy/__init__.py → update shim
```

**Actions**:
1. Read `trading_strategy/core.py`
2. Map to `src/app/domain/strategies/base.py`
3. Update `example_strategy.py` if needed
4. Create compatibility shim

**Verification**:
- Strategy signal generation unchanged
- Test with workflow execution

#### Task 3.4: Position Manager → Domain Position (45 min)
**Files to migrate** (2 files):
```
domain/position_manager/core.py → src/app/domain/position/*.py
domain/position_manager/__init__.py → update shim
```

**Actions**:
1. Read `position_manager/core.py`
2. Split between calculator.py and updater.py
3. Merge with existing files if overlap
4. Create compatibility shim

**Verification**:
- Position calculations correct
- Buy/sell quantity logic preserved

#### Task 3.5: Update Domain Shim (15 min)
**File**: `domain/__init__.py`

**Actions**:
1. Create comprehensive shim redirecting all domain imports
2. Test all legacy imports still work
3. Document mapping in comments

---

### Phase 4: Infrastructure Layer Migration (Day 1: Afternoon + Day 2: Morning)

#### Task 4.1: Redis Client → Persistence/Redis (2 hours)
**Files to migrate** (15 files):
```
infrastructure/external/redis_client/ → src/app/infrastructure/persistence/redis/
```

**Sub-tasks**:
1. **Core Connection** (30 min):
   - `client.py, core.py` → `connection/pool.py, connect.py`
   - Preserve connection pooling logic

2. **Repository Implementations** (45 min):
   - `trade_counter_repo.py` → extend `repos/trade_repo.py`
   - `cost_repo.py` → extend `repos/cost_repo.py`
   - `position_repo.py` → extend `repos/position_repo.py`
   - `price_repo.py` → extend `repos/price_repo.py`
   - `balance_cache.py, market_cache.py` → `repos/account_balance_repo.py, market_price_repo.py`

3. **Utility Modules** (30 min):
   - `position_layers_repo.py` → `repos/position_repo.py`
   - `bot_status_repo.py` → `repos/bot_state_repo.py`
   - `mexc_raw_repo.py` → `repos/raw_data_repo.py`

4. **Keys/Codecs** (15 min):
   - Verify `keys/account_keys.py, market_keys.py` are complete
   - Add any missing key patterns

**Verification**:
- All Redis operations work
- Connection pooling preserved
- No data loss in migration

#### Task 4.2: MEXC Client → Exchange/MEXC (2.5 hours)
**Files to migrate** (30+ files):
```
infrastructure/external/mexc_client/ → src/app/infrastructure/exchange/mexc/
```

**Sub-tasks**:
1. **HTTP Authentication** (30 min):
   - `utils/signature.py` → `http/auth/sign_request.py`
   - `utils/parser.py` → `_shared/response_parser.py`
   - `utils/types.py` → `_shared/types.py`

2. **Market Endpoints** (30 min):
   - `endpoints/market.py` → split into:
     - `http/market/get_price.py`
     - `http/market/get_orderbook.py`
     - `http/market/get_ticker.py`
     - `http/market/get_klines.py`

3. **Account Endpoints** (30 min):
   - `endpoints/account.py` → split into:
     - `http/account/get_balance.py`
     - `http/account/list_orders.py`
     - `http/account/get_account_info.py`

4. **Trade Endpoints** (30 min):
   - `endpoints/order.py` → split into:
     - `http/trade/place_order.py`
     - `http/trade/cancel_order.py`
     - `http/trade/query_order.py`

5. **WebSocket** (30 min):
   - `ws_client.py, ws_channels.py` → `ws/connect.py, handlers.py`

6. **Adapters** (30 min):
   - Create `adapters/market_adapter.py` (domain port implementation)
   - Create `adapters/account_adapter.py` (domain port implementation)

**Verification**:
- All API calls work
- Authentication preserved
- WebSocket connections stable

#### Task 4.3: Bot Runtime (1 hour)
**Files to migrate** (8 files):
```
infrastructure/bot/ → src/app/infrastructure/bot_runtime/
```

**Sub-tasks**:
1. **Core Logic** (30 min):
   - `bot_core/core.py` → merge into `lifecycle.py`
   - `bot_core/startup.py, cleanup.py` → `lifecycle.py`
   - `bot_core/execution.py` → `executor.py`

2. **Strategy/Risk** (20 min):
   - `bot_core/strategy.py, risk.py` → `risk_adapter.py`
   - `bot_core/data_collection.py` → distribute to appropriate modules

3. **Utils** (10 min):
   - `bot_utils.py` → evaluate and merge or create `_utils.py`

**Verification**:
- Bot start/stop works
- Scheduled execution preserved
- Risk checks integrated

#### Task 4.4: Config (15 min)
**Status**: Already mostly migrated

**Actions**:
1. Verify `src/app/infrastructure/config/` is complete
2. Check all environment variables handled
3. Update `infrastructure/config/` to shim

---

### Phase 5: Services Completion (Day 2: Late Morning)

#### Task 5.1: Market Services (45 min)
**Files** (10 files in `services/market/`):
```
services/market/market_service_core.py → src/app/application/market/
services/market/cache_*.py → evaluate necessity or merge
services/market/price_*.py → merge into get_price.py or helpers
```

**Actions**:
1. Read all market service files
2. Consolidate into application layer use cases
3. Create `_market_service.py` if shared logic needed
4. Update shims

**Verification**:
- Market data fetching works
- Caching behavior preserved
- Price updates functional

#### Task 5.2: Account Services (30 min)
**Files** (3 files in `services/account/`):
```
services/account/balance_service_core.py → Already done (shim exists)
```

**Actions**:
1. Verify balance service fully migrated
2. Check no additional account services needed
3. Update shims if missing

#### Task 5.3: Trading Service Core (45 min)
**File**: `services/trading/trading_service_core.py` (11939 bytes)

**Actions**:
1. Split into 3 files:
   - `_trading_service_init.py` - initialization logic
   - `_trading_service_execute.py` - execution logic
   - `_trading_service_finalize.py` - finalization logic
2. Create main `_trading_service.py` that imports all parts
3. Update imports in src/app files
4. Create shim

**Verification**:
- Trading execution unchanged
- Order placement works
- Position updates correct

---

### Phase 6: API Layer Migration (Day 2: Afternoon)

#### Task 6.1: Analyze API Dependencies (15 min)
**Action**: Map all imports in `/api/` to determine:
- Which use legacy infrastructure directly
- Which can be replaced by src/app modules
- Which need adapter creation

#### Task 6.2: Market Routes (1 hour)
**Files** (8 files in `api/market/`):

**Actions**:
1. For each route file:
   - Read handler logic
   - Map to `src/app/application/market/` use case
   - Update `src/app/interfaces/http/market.py`
2. Remove dependency on legacy handlers
3. Test each endpoint

#### Task 6.3: Account Routes (45 min)
**Files** (5 files in `api/account/`):

**Actions**:
1. Similar process to market routes
2. Update `src/app/interfaces/http/account.py`
3. Ensure balance, orders, trades all work

#### Task 6.4: Bot Routes (30 min)
**Files** (3 files in `api/bot/`):

**Actions**:
1. Update `src/app/interfaces/http/bot.py`
2. Connect to application layer bot use cases
3. Test start/stop/status

#### Task 6.5: Other Routes (30 min)
**Files**: Status, sub-account, etc.

**Actions**:
1. Update remaining route handlers
2. Connect to application layer
3. Test all endpoints

#### Task 6.6: Update main.py (15 min)
**Action**: Ensure main.py only imports from `src/app/interfaces/http/`

---

### Phase 7: Legacy Cleanup (Day 2: Late Afternoon)

#### Task 7.1: Verify No Active Imports (30 min)
**Actions**:
1. Search for imports from legacy directories:
   ```bash
   grep -r "from domain" src/ --include="*.py"
   grep -r "from infrastructure" src/ --include="*.py" | grep -v "from src"
   grep -r "from api\." src/ --include="*.py"
   grep -r "from services" src/ --include="*.py" | grep -v "from src"
   grep -r "from repositories" src/ --include="*.py" | grep -v "from src"
   ```
2. Fix any remaining imports

#### Task 7.2: Test Application (30 min)
**Actions**:
1. Run full test suite
2. Start application and test all endpoints
3. Verify bot execution works
4. Check logs for errors

#### Task 7.3: Remove Legacy Directories (15 min)
**Actions**:
1. Delete `/domain/` directory
2. Delete `/infrastructure/` directory  
3. Delete `/api/` directory
4. Delete `/services/` directory
5. Delete `/repositories/` directory

#### Task 7.4: Update Documentation (15 min)
**Actions**:
1. Update README.md with new structure
2. Add migration completion note
3. Update ARCHITECTURE_TREE.md status

---

## Execution Strategy

### Daily Schedule

**Day 1** (Morning: 3.5 hours)
- 09:00-10:00: Phase 3.1 - Domain Interfaces
- 10:00-10:45: Phase 3.2 - Risk Manager
- 10:45-11:30: Phase 3.3 - Trading Strategy
- 11:30-12:15: Phase 3.4 - Position Manager
- 12:15-12:30: Phase 3.5 - Domain Shim

**Day 1** (Afternoon: 3.5 hours)
- 13:30-15:30: Phase 4.1 - Redis Client
- 15:30-18:00: Phase 4.2 - MEXC Client (Part 1)

**Day 2** (Morning: 3.5 hours)
- 09:00-10:00: Phase 4.2 - MEXC Client (Part 2)
- 10:00-11:00: Phase 4.3 - Bot Runtime
- 11:00-11:45: Phase 5.1 - Market Services
- 11:45-12:15: Phase 5.2 - Account Services
- 12:15-13:00: Phase 5.3 - Trading Service Core

**Day 2** (Afternoon: 3.5 hours)
- 14:00-14:15: Phase 6.1 - API Analysis
- 14:15-15:15: Phase 6.2 - Market Routes
- 15:15-16:00: Phase 6.3 - Account Routes
- 16:00-16:30: Phase 6.4 - Bot Routes
- 16:30-17:00: Phase 6.5 - Other Routes
- 17:00-17:15: Phase 6.6 - Update main.py
- 17:15-18:00: Phase 7 - Cleanup & Testing

### Commit Strategy

**Commit after each phase** with message format:
```
Migrate [layer] to src/app: [specific component]

- Migrated X files from [legacy] to [new location]
- Created compatibility shims for backward compatibility
- All tests passing, no breaking changes

Phase: X.Y [component name]
```

### Testing Strategy

**Test after each major component**:
1. Run `pytest tests/` for unit tests
2. Manual API endpoint testing with curl/Postman
3. Check application startup
4. Monitor logs for warnings/errors

---

## Risk Mitigation

### File Size Constraint
- **Risk**: Some files exceed 4000 bytes
- **Mitigation**: Split large files proactively during migration
- **Fallback**: Leave in legacy location with updated imports

### Import Circular Dependencies
- **Risk**: New structure may create circular imports
- **Mitigation**: Use forward references and TYPE_CHECKING
- **Fallback**: Restructure to break cycles

### Breaking Changes
- **Risk**: Migration breaks existing functionality
- **Mitigation**: Comprehensive shims + incremental testing
- **Fallback**: Revert specific component if issues found

### Time Overrun
- **Risk**: Migration takes longer than estimated
- **Mitigation**: Focus on high-priority items first
- **Fallback**: Pause at phase boundaries, resume later

---

## Success Metrics

- ✅ All 142 legacy Python files migrated to src/app
- ✅ Zero imports from legacy directories in src/app
- ✅ All tests passing
- ✅ Application starts and runs without errors
- ✅ All HTTP endpoints functional
- ✅ Bot execution works
- ✅ Legacy directories removed
- ✅ Documentation updated

---

## Post-Migration Tasks

1. **Performance Review**: Check if new structure impacts performance
2. **Code Coverage**: Ensure test coverage maintained or improved
3. **Documentation**: Create architecture decision records (ADR)
4. **Team Training**: Brief team on new structure
5. **CI/CD Update**: Update deployment scripts if needed

---

## Quick Reference: File Mapping

| Legacy Location | New Location | Priority |
|----------------|--------------|----------|
| `domain/interfaces/` | `src/app/domain/ports/` | HIGH |
| `domain/risk_manager/` | `src/app/domain/risk/` | HIGH |
| `domain/trading_strategy/` | `src/app/domain/strategies/` | HIGH |
| `domain/position_manager/` | `src/app/domain/position/` | HIGH |
| `infrastructure/external/redis_client/` | `src/app/infrastructure/persistence/redis/` | HIGH |
| `infrastructure/external/mexc_client/` | `src/app/infrastructure/exchange/mexc/` | HIGH |
| `infrastructure/bot/` | `src/app/infrastructure/bot_runtime/` | MEDIUM |
| `services/market/` | `src/app/application/market/` | MEDIUM |
| `services/trading/` | `src/app/application/trading/` | MEDIUM |
| `api/` | `src/app/interfaces/http/` | MEDIUM |

---

**Total Estimated Time**: 14 hours = 1.75 work days
**Buffer**: +0.25 days for unexpected issues
**Total**: 2 work days

---

*Generated: 2025-12-31*
*For: qrl-api architecture migration*
*Scope: Complete migration of 142 legacy files to src/app structure*
