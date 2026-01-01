# Refactoring Roadmap - Phase 2 Outcomes

**Created**: 2024-12-31  
**Based On**: Phase 2 Module Analysis Report  
**Total Effort**: ~15 hours over 2 weeks

## Overview

This roadmap provides a prioritized, actionable plan for splitting the 11 modules that exceed the 4KB file size guideline. Each refactoring is designed to be incremental, testable, and low-risk.

## Priority 1: Critical - Week 1

### 1.1 trading_service_core.py (12KB → 4x ~3KB)

**Location**: `src/app/application/trading/services/trading/`  
**Effort**: 3 hours  
**Risk**: MEDIUM  
**Priority**: CRITICAL

**Current Structure**:
- Single 12KB file orchestrating entire trading workflow

**Target Structure**:
```
trading/
├── trading_orchestrator.py     (3KB) - Main workflow coordination
├── trading_validators.py       (2.5KB) - Input validation
├── trading_executor.py          (3KB) - Trade execution
├── trading_monitor.py           (2.5KB) - Status monitoring
└── trading_service_core.py      (1KB) - Facade/exports
```

**Steps**:
1. Extract validation logic to `trading_validators.py`
2. Extract execution logic to `trading_executor.py`
3. Extract monitoring logic to `trading_monitor.py`
4. Keep orchestration in `trading_orchestrator.py`
5. Update `trading_service_core.py` to re-export
6. Update all imports
7. Run full test suite

**Test Strategy**:
- Maintain 100% behavioral equivalence
- Add integration tests for workflow
- No changes to public API

## Priority 2: High - Week 1-2

### 2.1 market.py HTTP routes (6KB → 3x ~2KB)

**Location**: `src/app/interfaces/http/`  
**Effort**: 2 hours  
**Risk**: LOW

**Target Structure**:
```
http/market/
├── price.py          (2KB) - /price, /ticker endpoints
├── orderbook.py      (2KB) - /orderbook, /depth endpoints
├── klines.py         (2KB) - /klines, /trades endpoints
└── __init__.py       (0.5KB) - Router aggregation
```

**Steps**:
1. Create `market/` subdirectory
2. Split endpoints by resource type
3. Update router to include sub-routers
4. Update tests

### 2.2 settings.py (5.8KB → 3x ~2KB)

**Location**: `src/app/infrastructure/config/`  
**Effort**: 1 hour  
**Risk**: LOW

**Target Structure**:
```
config/
├── settings_base.py         (2KB) - Common settings
├── settings_production.py   (2KB) - Production overrides
├── settings_development.py  (2KB) - Development overrides
└── settings.py              (0.5KB) - Environment selector
```

### 2.3 sub_account.py HTTP routes (5.5KB → 3x ~2KB)

**Location**: `src/app/interfaces/http/`  
**Effort**: 2 hours  
**Risk**: LOW

**Target Structure**:
```
http/sub_account/
├── management.py    (2KB) - CRUD operations
├── balance.py       (2KB) - Balance operations
├── keys.py          (1.5KB) - API key management
└── __init__.py      (0.5KB) - Router aggregation
```

### 2.4 trading_workflow.py (5.3KB → Keep + extract phases)

**Location**: `src/app/application/trading/services/trading/`  
**Effort**: 2 hours  
**Risk**: MEDIUM

**Target Structure**:
```
trading/
├── workflow/
│   ├── orchestrator.py         (2KB) - Main workflow
│   ├── phase_startup.py        (1KB) - Phase 1
│   ├── phase_data_collection.py (1KB) - Phase 2
│   ├── phase_strategy.py       (1KB) - Phase 3
│   └── ...
└── trading_workflow.py         (1KB) - Facade
```

### 2.5 Redis cache helpers (6KB + 5.6KB → 4x ~3KB each)

**Location**: `src/app/infrastructure/persistence/redis/cache/`  
**Effort**: 3 hours (both files)  
**Risk**: LOW

**Target Structure**:
```
cache/
├── market/
│   ├── read.py      (3KB) - Read operations
│   └── write.py     (3KB) - Write operations
├── balance/
│   ├── read.py      (3KB) - Read operations
│   └── write.py     (3KB) - Write operations
├── market.py        (0.5KB) - Re-exports
└── balance.py       (0.5KB) - Re-exports
```

### 2.6 trade_repository_core.py (5KB → 2x ~2.5KB)

**Location**: `src/app/infrastructure/persistence/repos/trade/`  
**Effort**: 1.5 hours  
**Risk**: LOW

**Target Structure**:
```
trade/
├── trade_repository_read.py   (2.5KB) - Query operations
├── trade_repository_write.py  (2.5KB) - Write operations
└── trade_repository_core.py   (0.5KB) - Facade
```

## Priority 3: Medium - Week 2

### 3.1 account.py HTTP routes (4.5KB)
### 3.2 market_service_core.py (4.5KB)
### 3.3 redis_data_manager.py (4.2KB)

**Status**: MONITOR  
**Action**: Watch for growth; split if exceeds 5KB

## Priority 4: Optional - Future

### 4.1 SRP Violation - keys.py

**Location**: `src/app/infrastructure/utils/`  
**Effort**: 30 minutes  
**Priority**: LOW

**Current**: Validation + Persistence in one file  
**Recommended**: Extract if time permits, not critical

## Implementation Guidelines

### Before Starting Each Refactoring

1. ✅ Read the module completely
2. ✅ Identify natural seams/boundaries
3. ✅ Create ADR documenting decision
4. ✅ Write splitting plan with test strategy
5. ✅ Get approval if MEDIUM+ risk

### During Refactoring

1. ✅ Work on feature branch
2. ✅ Split incrementally (one extraction at a time)
3. ✅ Run tests after each extraction
4. ✅ Maintain public API compatibility
5. ✅ Update documentation inline

### After Refactoring

1. ✅ Run full test suite
2. ✅ Check import paths updated
3. ✅ Verify no circular dependencies
4. ✅ Update architecture documentation
5. ✅ Deploy to staging first
6. ✅ Monitor for 48 hours before production

## Success Criteria

### Per Refactoring

- ✅ All files <4KB
- ✅ Test coverage maintained or improved
- ✅ No behavioral changes
- ✅ No new circular dependencies
- ✅ Import paths updated throughout

### Overall

- ✅ 0 modules >4KB
- ✅ 0 CRITICAL/HIGH SRP violations
- ✅ <5 MEDIUM SRP violations
- ✅ Test coverage ≥80%
- ✅ Container startup <5s

## Risk Mitigation

### High-Risk Refactorings

**trading_service_core.py** and **trading_workflow.py**:
- Feature flag all changes
- Canary deploy (10% → 50% → 100%)
- Keep original code for 1 week
- Comprehensive integration tests

### Low-Risk Refactorings

**HTTP routes**, **config**, **cache helpers**:
- Standard review process
- Standard deployment
- Standard monitoring

## Timeline

### Week 1 (Dec 31 - Jan 6)

- Day 1-2: trading_service_core.py split (CRITICAL)
- Day 3: settings.py split
- Day 4: market.py HTTP split
- Day 5: Testing and validation

### Week 2 (Jan 7 - Jan 13)

- Day 1-2: sub_account.py + trading_workflow.py
- Day 3-4: Redis cache splits
- Day 5: trade_repository_core.py
- Day 6-7: Testing, documentation, deployment

## Tracking

| Module | Size | Priority | Status | Assignee | Completion |
|--------|------|----------|--------|----------|------------|
| trading_service_core.py | 12KB | CRITICAL | 🔵 Planned | TBD | - |
| market.py (HTTP) | 6KB | HIGH | 🔵 Planned | TBD | - |
| market.py (cache) | 6KB | HIGH | 🔵 Planned | TBD | - |
| settings.py | 5.8KB | HIGH | 🔵 Planned | TBD | - |
| balance.py (cache) | 5.6KB | HIGH | 🔵 Planned | TBD | - |
| sub_account.py | 5.5KB | HIGH | 🔵 Planned | TBD | - |
| trading_workflow.py | 5.3KB | HIGH | 🔵 Planned | TBD | - |
| trade_repository_core.py | 5KB | HIGH | 🔵 Planned | TBD | - |

**Status Legend**:
- 🔵 Planned
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked

## Next Actions

1. **Review & Approve** this roadmap
2. **Create ADR** for trading_service_core.py split
3. **Assign** refactorings to team members
4. **Begin Week 1** execution

---

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2024-12-31  
**Next Review**: After Week 1 completion
