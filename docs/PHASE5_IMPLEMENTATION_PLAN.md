# Phase 5: Import Updates Implementation Plan

**Status**: READY TO EXECUTE  
**Complexity**: 9/10 (Highest complexity phase)  
**Estimated Time**: 2-3 days  
**Created**: 2026-01-02  
**Methodology**: Sequential Thinking + Software Planning Tool

---

## Overview

Phase 5 systematically updates ALL import statements across the codebase to reference new Clean Architecture-compliant paths from Phases 1-4.

**Strategy**: Bottom-up, layer-by-layer with incremental validation

---

## Tasks (15 Total)

### Group 1: Domain Verification (30 min)

**Task 5.2**: Verify domain has zero external dependencies
- Check no imports from application/infrastructure/interfaces
- Domain should be self-contained

### Group 2: Infrastructure (4 hours)

**Task 5.3**: Update infrastructure domain imports (2h)
- Files: infrastructure/external/mexc/, supabase/
- Pattern: domain.models → domain.trading.entities

**Task 5.4**: Update infrastructure application imports (1h)
- Files: Adapters, infrastructure services
- Pattern: domain.ports → application.trading.ports

**Task 5.5**: Validate infrastructure layer (1h)

### Group 3: Application (6 hours)

**Task 5.6**: Update application domain imports (2h)
- Files: use_cases/, services/
- Pattern: domain.models → domain.trading.entities

**Task 5.7**: Update application internal imports (2h) **CRITICAL**
- Pattern: application.account → application.trading.use_cases
- Pattern: application.market → application.trading.use_cases

**Task 5.8**: Update application infrastructure imports (1h)

**Task 5.9**: Validate application layer (1h)

### Group 4: Interfaces (4 hours)

**Task 5.10**: Update HTTP routes ✅ PARTIAL (bebbc25)
**Task 5.11**: Update tasks/background ✅ PARTIAL (bebbc25)
**Task 5.12**: Validate interfaces layer (2h) **CRITICAL**

### Group 5: Tests (4 hours)

**Task 5.13**: Update test domain imports (1h)
**Task 5.14**: Update test application imports (2h)
**Task 5.15**: Full test suite validation (1h) **CRITICAL**

---

## Execution Order

1. Domain verification → 2. Infrastructure → 3. Application → 4. Interfaces → 5. Tests
2. Validate after each group
3. Commit incrementally

---

## Success Criteria

- [ ] All files compile
- [ ] Zero old import patterns
- [ ] Application starts
- [ ] 64+ tests pass
- [ ] Cloud Run deploys

**Estimated**: 20 hours (2.5 days)
