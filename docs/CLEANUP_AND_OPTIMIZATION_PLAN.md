# Cleanup and Optimization Plan

## Executive Summary

This plan addresses the removal of backward compatibility wrappers and establishes a systematic framework for continuous codebase optimization following Occam's Razor principles. The goal is to achieve a minimal, verifiable structure that satisfies current needs while remaining adaptable to change.

## Current State Analysis

### Remaining Legacy Files (28 total)

**Infrastructure Compatibility Wrappers (3 files)**
- `infrastructure/__init__.py` (67 bytes) - Empty wrapper
- `infrastructure/bot.py` (179 bytes) - TradingBot delegation
- `infrastructure/external/__init__.py` (711 bytes) - MEXCClient/RedisClient re-exports

**Services Compatibility Wrappers (25 files)**
- `services/__init__.py` (576 bytes) - Service aggregation
- `services/trading/` (11 files) - Trading service implementation
- `services/market/` (7 files) - Market service implementation
- `services/account/` (3 files) - Account service implementation

### Legacy Import References (31 found)

**Test Files (8 imports)**
- `tests/test_ws_client.py` - mexc_client.ws_client
- `tests/test_account_routes.py` - mexc_client.account
- `tests/test_module_imports.py` - infrastructure.external, redis_client
- `tests/test_balance_helpers.py` - mexc_client.account, services.account
- `tests/test_mexc_client_core.py` - mexc_client.core, signer

**Application Code (23 imports)**
- `src/app/interfaces/http/account.py` - mexc_client.account.QRL_USDT_SYMBOL
- `src/app/infrastructure/exchange/mexc/` - Various mexc_client imports (20 files)

## Phase 1: Compatibility Wrapper Cleanup (IMMEDIATE)

**Objective**: Remove all backward compatibility wrappers and update imports to use new architecture paths.

### Step 1.1: Update Test Imports (Est: 30min)

**Files to Update (5 files)**:
1. `tests/test_ws_client.py`
2. `tests/test_account_routes.py`
3. `tests/test_module_imports.py`
4. `tests/test_balance_helpers.py`
5. `tests/test_mexc_client_core.py`

**Changes**:
```python
# Before
from infrastructure.external.mexc_client import mexc_client
from services.account import BalanceService

# After
from src.app.infrastructure.external.mexc import mexc_client
from src.app.application.trading.services.account import BalanceService
```

### Step 1.2: Update Application Imports (Est: 45min)

**Files to Update (21 files)**:
- `src/app/interfaces/http/account.py` (1 file)
- `src/app/infrastructure/exchange/mexc/` (20 files)

**Changes**:
```python
# Before
from infrastructure.external.mexc_client import MEXCClient, mexc_client
from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL

# After
from src.app.infrastructure.external.mexc import MEXCClient, mexc_client
from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL
```

### Step 1.3: Remove Compatibility Wrappers (Est: 15min)

**Files to Delete (28 files)**:
```
infrastructure/__init__.py
infrastructure/bot.py
infrastructure/external/__init__.py
services/__init__.py
services/trading/ (11 files)
services/market/ (7 files)
services/account/ (3 files)
```

**Validation**:
```bash
# Verify no remaining legacy imports
grep -r "from infrastructure\." src/ tests/ --include="*.py"
grep -r "from services\." src/ tests/ --include="*.py"

# Should return zero results
```

### Step 1.4: Verification & Testing (Est: 30min)

**Test Suite**:
```bash
# Run all tests
pytest tests/ -v

# Verify container builds
docker build -t qrl-api-test .

# Verify container starts
docker run -p 8080:8080 -e PORT=8080 qrl-api-test

# Startup time should be <5s
```

**Success Criteria**:
- ✅ All tests pass
- ✅ Zero legacy imports found
- ✅ Container starts successfully
- ✅ Health check responds within 5s

**Estimated Total Time**: 2 hours

---

## Phase 2: Module Responsibility Analysis (SRP Validation)

**Objective**: Ensure each module has a single, well-defined responsibility following the Single Responsibility Principle.

### Analysis Framework

**Step 2.1: Module Inventory (Est: 1h)**

Create comprehensive module map:
```bash
python docs/optimization/analyze_modules.py > docs/optimization/module_inventory.md
```

**Output**: Module inventory with:
- Module path
- Primary responsibility
- Public API surface (exported functions/classes)
- Dependencies (imports)
- File size
- Complexity metrics (functions, classes, LOC)

### Step 2.2: SRP Violation Detection (Est: 2h)

**Criteria for SRP Violation**:
1. Module has >3 primary responsibilities
2. Module name is vague (e.g., "utils", "helpers", "common")
3. Module has >10 public functions with unrelated purposes
4. Module file size >4KB with mixed concerns

**Analysis Script**:
```python
# docs/optimization/analyze_srp.py
def analyze_srp_violations():
    """
    Analyzes modules for Single Responsibility Principle violations.
    Returns list of modules with multiple responsibilities.
    """
    violations = []
    for module in get_all_modules():
        responsibilities = identify_responsibilities(module)
        if len(responsibilities) > 1:
            violations.append({
                'module': module,
                'responsibilities': responsibilities,
                'recommendation': suggest_split(module, responsibilities)
            })
    return violations
```

### Step 2.3: Refactoring Candidates (Est: 1h)

**Expected Findings**:
- Service layer consolidation opportunities
- Repository interface/core splits that can merge
- Utility modules that need domain-specific homes

**Action Items**:
- Document refactoring opportunities
- Create ADRs for significant splits/merges
- Prioritize by impact and risk

**Estimated Total Time**: 4 hours

---

## Phase 3: Coupling & Dependency Analysis

**Objective**: Identify and prevent problematic dependencies (circular, hidden, cross-layer).

### Step 3.1: Dependency Graph Generation (Est: 30min)

```bash
python docs/optimization/generate_dependency_graph.py
```

**Output**:
- `docs/optimization/dependency_graph.png` - Visual dependency map
- `docs/optimization/dependency_matrix.md` - Module dependency matrix
- `docs/optimization/circular_deps.md` - Circular dependency report

### Step 3.2: Architectural Layer Validation (Est: 1h)

**Layer Rules**:
```
interfaces/http → application → domain
              ↓            ↓        
         infrastructure ← ← ← ← (NO UPWARD DEPS)
```

**Validation Script**:
```python
# docs/optimization/validate_layers.py
def validate_layer_dependencies():
    """
    Ensures dependencies only flow inward in clean architecture.
    Infrastructure should never import from domain/application/interfaces.
    """
    violations = []
    for module in get_infrastructure_modules():
        for import_stmt in get_imports(module):
            if is_domain_or_application_import(import_stmt):
                violations.append({
                    'module': module,
                    'illegal_import': import_stmt,
                    'rule': 'Infrastructure cannot depend on domain/application'
                })
    return violations
```

### Step 3.3: Coupling Metrics (Est: 1h)

**Metrics to Track**:
- **Afferent Coupling (Ca)**: # of modules that depend on this module
- **Efferent Coupling (Ce)**: # of modules this module depends on
- **Instability (I)**: Ce / (Ce + Ca) - should be 0 for stable, 1 for volatile
- **Abstractness (A)**: # abstract classes / total classes

**Target Zones**:
- Domain: Low instability (0.0-0.3), High abstractness (0.7-1.0)
- Infrastructure: High instability (0.7-1.0), Low abstractness (0.0-0.3)

### Step 3.4: Hidden Dependency Detection (Est: 1h)

**Detect**:
- Global state access
- Singleton pattern abuse
- Hard-coded configuration
- Direct database/external API calls from business logic

**Estimated Total Time**: 3.5 hours

---

## Phase 4: Dead Code Detection & Removal

**Objective**: Identify and remove unused code to maintain codebase simplicity.

### Step 4.1: Import Analysis (Est: 30min)

**Find unused imports**:
```bash
autoflake --check --recursive src/ tests/
```

### Step 4.2: Function/Class Usage Analysis (Est: 2h)

**Analysis Script**:
```python
# docs/optimization/find_dead_code.py
def find_unused_definitions():
    """
    Finds functions and classes that are never imported or called.
    Uses AST analysis to track definitions and references.
    """
    all_definitions = collect_all_definitions()
    all_references = collect_all_references()
    
    unused = []
    for definition in all_definitions:
        if definition not in all_references:
            if not is_public_api(definition):
                unused.append(definition)
    
    return unused
```

### Step 4.3: Safe Removal Process (Est: 1h)

**Process**:
1. Identify unused code
2. Verify not part of public API
3. Check git history for recent usage
4. Remove with commit message linking to analysis
5. Run full test suite
6. Monitor for 1 week before considering permanent

**Estimated Total Time**: 3.5 hours

---

## Phase 5: Duplication Detection & DRY Enforcement

**Objective**: Identify and consolidate duplicated code following DRY principles.

### Step 5.1: Clone Detection (Est: 1h)

**Tools**:
```bash
# Find exact duplicates
vulture src/

# Find similar code blocks
duplo src/ tests/
```

### Step 5.2: Pattern Extraction (Est: 3h)

**Common Patterns to Extract**:
1. Error handling wrappers
2. Logging patterns
3. Validation logic
4. Data transformation functions
5. API response formatting

**Extraction Process**:
```python
# Before (duplicated in 3 files)
try:
    result = await some_operation()
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"success": False, "error": str(e)}

# After (extracted to utility)
@handle_errors
async def some_operation():
    return await some_operation_impl()
```

### Step 5.3: Consolidation Roadmap (Est: 1h)

**Action Items**:
- Document duplication hotspots
- Create reusable utility functions
- Update all callsites
- Verify behavioral equivalence

**Estimated Total Time**: 5 hours

---

## Phase 6: Architecture Guard Enhancement

**Objective**: Automated enforcement of architecture rules to prevent regression.

### Step 6.1: Extend Architecture Guard (Est: 2h)

**New Rules to Add**:
```python
# architecture_guard.py additions

def check_no_legacy_imports():
    """Ensure no imports from infrastructure/ or services/ root"""
    violations = []
    for file in get_python_files():
        legacy_imports = find_legacy_imports(file)
        if legacy_imports:
            violations.append(f"{file}: {legacy_imports}")
    return violations

def check_layer_dependencies():
    """Ensure dependencies only flow inward"""
    # Implementation from Phase 3

def check_circular_dependencies():
    """Detect circular import chains"""
    # Implementation from Phase 3

def check_file_size_limit():
    """Ensure no file exceeds 4KB"""
    violations = []
    for file in get_python_files():
        if get_file_size(file) > 4000:
            violations.append(f"{file}: {get_file_size(file)} bytes")
    return violations
```

### Step 6.2: CI Integration (Est: 1h)

**GitHub Actions Workflow**:
```yaml
# .github/workflows/architecture-guard.yml
name: Architecture Guard
on: [push, pull_request]
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Architecture Guard
        run: python architecture_guard.py
      - name: Check for violations
        run: |
          if [ -f violations.txt ]; then
            cat violations.txt
            exit 1
          fi
```

**Estimated Total Time**: 3 hours

---

## Phase 7: Test Coverage & Behavioral Validation

**Objective**: Ensure refactoring doesn't change external behavior.

### Step 7.1: Coverage Analysis (Est: 1h)

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

**Target Coverage**:
- Domain layer: 90%
- Application layer: 85%
- Infrastructure layer: 75%
- Overall: 80%

### Step 7.2: Behavioral Tests (Est: 4h)

**Add integration tests for key flows**:
```python
# tests/integration/test_trading_flow.py
def test_complete_trading_cycle():
    """
    Ensures end-to-end trading flow works correctly.
    Tests: data fetch → strategy → risk → execution → cleanup
    """
    # Setup
    # Execute
    # Assert behavior matches expectations
```

### Step 7.3: Contract Tests (Est: 2h)

**Public API contracts**:
```python
# tests/contracts/test_api_contracts.py
def test_market_endpoints_contract():
    """Ensures API responses match expected schema"""
    # Test all endpoints
    # Validate response schemas
    # Check backward compatibility
```

**Estimated Total Time**: 7 hours

---

## Phase 8: Documentation & Knowledge Capture

**Objective**: Document simplification decisions and architectural rationale.

### Step 8.1: Architecture Decision Records (Est: 3h)

**Create ADRs for**:
- `docs/adr/001-clean-architecture-adoption.md`
- `docs/adr/002-backward-compatibility-removal.md`
- `docs/adr/003-service-layer-consolidation.md`
- `docs/adr/004-file-size-limit-rationale.md`

**Template**:
```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[Problem description and constraints]

## Decision
[What we decided and why]

## Consequences
[Positive and negative outcomes]

## Alternatives Considered
[Other options and why rejected]
```

### Step 8.2: Developer Guide Updates (Est: 2h)

**Update**:
- `README.md` - Remove legacy references
- `ARCHITECTURE_TREE.md` - Reflect final structure
- `CONTRIBUTING.md` - Add architecture rules

### Step 8.3: Inline Code Documentation (Est: 2h)

**Add docstrings where missing**:
- Module-level purpose statements
- Function/class docstrings with examples
- Complex algorithm explanations

**Estimated Total Time**: 7 hours

---

## Implementation Timeline

### Week 1: Cleanup & Foundation
- **Day 1**: Phase 1 - Compatibility wrapper cleanup (2h)
- **Day 2**: Phase 6 - Architecture guard enhancement (3h)
- **Day 3**: Phase 7 - Test coverage baseline (7h)
- **Day 4**: Phase 2 - Module responsibility analysis (4h)
- **Day 5**: Buffer for issues

### Week 2: Analysis & Optimization
- **Day 1**: Phase 3 - Coupling analysis (3.5h)
- **Day 2**: Phase 4 - Dead code detection (3.5h)
- **Day 3**: Phase 5 - Duplication detection (5h)
- **Day 4**: Phase 8 - Documentation (7h)
- **Day 5**: Buffer for issues

**Total Estimated Effort**: 38.5 hours

---

## Success Metrics

### Immediate (Phase 1)
- ✅ Zero legacy imports: `grep -r "from infrastructure\." src/ tests/ == 0`
- ✅ Zero backward compat wrappers: `ls infrastructure/ services/ == 0`
- ✅ All tests pass: `pytest tests/ == 100% success`
- ✅ Container starts: `docker run ... exits with 0`

### Short-term (Phases 2-5)
- ✅ All files <4KB: `find src/ -size +4k == 0`
- ✅ No circular dependencies: `analyze_deps.py == 0 cycles`
- ✅ SRP violations <5: `analyze_srp.py | wc -l < 5`
- ✅ Code duplication <10%: `duplo src/ < 10%`

### Long-term (Phases 6-8)
- ✅ Test coverage ≥80%: `pytest --cov src/ >= 80%`
- ✅ Architecture guard in CI: `GitHub Actions status = pass`
- ✅ ADRs for major decisions: `ls docs/adr/*.md >= 4`
- ✅ No failing architectural rules: `architecture_guard.py == 0`

---

## Rollback Strategy

### If Phase 1 Fails
```bash
# Restore compatibility wrappers
git checkout HEAD~1 infrastructure/ services/

# Revert import changes
git checkout HEAD~1 tests/ src/
```

### If Tests Fail After Refactoring
1. Identify failing test
2. Check if test needs update or code has regression
3. Fix or revert specific change
4. Re-run tests
5. Document lesson learned

### If Container Fails to Start
1. Check logs: `docker logs [container_id]`
2. Verify file permissions
3. Check template paths
4. Revert to last working commit
5. Investigate root cause

---

## Risk Mitigation

### High Risk: Breaking Production
**Mitigation**:
- All changes behind feature flags
- Canary deployments (10% → 50% → 100%)
- Automated rollback on error rate spike
- Comprehensive smoke tests

### Medium Risk: Test Suite False Negatives
**Mitigation**:
- Add integration tests for critical paths
- Manual testing of key user flows
- Load testing before prod deployment

### Low Risk: Documentation Drift
**Mitigation**:
- Link docs to code in CI
- Review docs in every PR
- Quarterly documentation audit

---

## Next Steps (Immediate Actions)

1. **Review & Approve Plan** (30min)
   - Stakeholder review
   - Timeline adjustment
   - Resource allocation

2. **Create Analysis Scripts** (2h)
   - `docs/optimization/analyze_modules.py`
   - `docs/optimization/analyze_srp.py`
   - `docs/optimization/generate_dependency_graph.py`
   - `docs/optimization/find_dead_code.py`

3. **Execute Phase 1** (2h)
   - Update all imports
   - Remove compatibility wrappers
   - Verify tests pass
   - Deploy to staging

4. **Baseline Metrics** (1h)
   - Run all analysis scripts
   - Document current state
   - Set improvement targets

**Ready to begin Phase 1 execution immediately upon approval.**
