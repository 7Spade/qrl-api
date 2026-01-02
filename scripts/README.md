# Architecture Restructuring Scripts

Automation scripts for restructuring the QRL Trading API according to ✨.md Clean Architecture specifications.

## Overview

These scripts automate the phased restructuring process documented in:
- `docs/ARCHITECTURE_RESTRUCTURE_PLAN.md` - Detailed implementation plan
- `docs/ARCHITECTURE_RESTRUCTURE_DIAGRAM.md` - Visual guide with diagrams
- `docs/✨.md` - Target architecture specification

## Safety Features

All scripts include:
- **Dry-run mode**: Preview changes before applying
- **Interactive confirmation**: Requires explicit "yes" for execution
- **Detailed reporting**: Shows all changes made
- **Error handling**: Stops on errors with clear messages
- **Incremental execution**: Can be safely interrupted and resumed

## Available Scripts

### Phase 1: Domain Layer Restructuring

**Script**: `restructure_phase1_domain.py`

Reorganizes the domain layer according to ✨.md specifications.

**What it does**:
- Creates `domain/trading/` directory structure
- Sets up `entities/`, `value_objects/`, `strategies/`, `services/`, `events/`
- Generates `repositories.py` with abstract repository interfaces
- Generates `errors.py` with domain exception definitions
- Creates proper `__init__.py` files with exports

**Usage**:
```bash
# Preview changes (ALWAYS run this first)
python scripts/restructure_phase1_domain.py --dry-run

# Apply changes (after reviewing dry-run output)
python scripts/restructure_phase1_domain.py --execute
```

**Expected output**:
```
Starting Phase 1 Domain Restructuring...
Root path: /home/runner/work/qrl-api/qrl-api
Mode: DRY RUN

[DRY RUN] Would create: .../domain/trading/entities
[DRY RUN] Would create: .../domain/trading/value_objects
...
[DRY RUN] Would create: .../domain/trading/repositories.py
[DRY RUN] Would create: .../domain/trading/errors.py

================================================================
PHASE 1 RESTRUCTURING REPORT
================================================================

Mode: DRY RUN
Total changes: 15

  CREATE DIR: .../domain/trading/entities
  CREATE DIR: .../domain/trading/value_objects
  ...

================================================================

✅ Dry run completed successfully
To apply changes, run with --execute flag
```

**After execution**:
1. Review generated files in `src/app/domain/trading/`
2. Manually move existing files to new locations (see checklist below)
3. Update imports in affected files
4. Run tests: `pytest tests/domain/ -v`
5. Commit changes: `git add . && git commit -m "refactor: Phase 1 domain restructure"`

### File Movement Checklist (Manual)

After running Phase 1 script, manually move these files:

#### Entities
```bash
# Move entities from models/ to trading/entities/
mv src/app/domain/models/order.py src/app/domain/trading/entities/
mv src/app/domain/models/trade.py src/app/domain/trading/entities/
mv src/app/domain/models/position.py src/app/domain/trading/entities/
mv src/app/domain/models/account.py src/app/domain/trading/entities/
```

#### Value Objects
```bash
# Move value objects from models/ to trading/value_objects/
mv src/app/domain/models/price.py src/app/domain/trading/value_objects/
mv src/app/domain/models/balance.py src/app/domain/trading/value_objects/
```

#### Strategies
```bash
# Move entire strategies directory
mv src/app/domain/strategies/* src/app/domain/trading/strategies/
```

#### Events
```bash
# Move entire events directory
mv src/app/domain/events/* src/app/domain/trading/events/
```

#### Services
```bash
# Move position services
mv src/app/domain/position/calculator.py src/app/domain/trading/services/position/
mv src/app/domain/position/updater.py src/app/domain/trading/services/position/

# Move risk services
mv src/app/domain/risk/limits.py src/app/domain/trading/services/risk/
mv src/app/domain/risk/stop_loss.py src/app/domain/trading/services/risk/
mv src/app/domain/risk/validators/* src/app/domain/trading/services/risk/validators/
```

#### Cleanup Old Directories
```bash
# After verifying all files are moved, remove old directories
rm -rf src/app/domain/models/
rm -rf src/app/domain/position/
rm -rf src/app/domain/risk/
rm -rf src/app/domain/strategies/
rm -rf src/app/domain/events/
```

### Import Update Pattern

After moving files, update imports using this pattern:

**Before**:
```python
from src.app.domain.models.order import Order
from src.app.domain.models.price import Price
from src.app.domain.strategies.base import Strategy
```

**After**:
```python
from src.app.domain.trading.entities.order import Order
from src.app.domain.trading.value_objects.price import Price
from src.app.domain.trading.strategies.base import Strategy
```

Use find/replace or this command:
```bash
# Find all files that need import updates
grep -r "from src.app.domain.models" src/app/

# Example sed command (test on one file first!)
sed -i 's/from src.app.domain.models.order/from src.app.domain.trading.entities.order/g' filename.py
```

## Future Scripts (Coming Soon)

### Phase 2: Application Layer Restructuring
- Consolidates `account/`, `bot/`, `market/` into `trading/`
- Creates `use_cases/`, `services/`, `ports/`, `dtos/`, `commands/`
- Moves `domain/ports/` to `application/trading/ports/`

### Phase 3: Infrastructure Consolidation
- Merges `external/mexc/` and `exchange/mexc/`
- Ensures proper MEXC structure: rest_client, ws_client, signer, adapters

### Phase 4: Interfaces Layer Updates
- Renames `tasks/` to `background/`
- Creates `websocket/` and `cli/` directories if needed

### Phase 5: Import Updates & Testing
- Automated import path updates
- Dependency injection configuration updates
- Full test suite validation

## Validation

After each phase, validate the changes:

```bash
# Run tests
pytest tests/domain/ -v

# Check for import errors
python -m py_compile src/app/domain/**/*.py

# Check for architecture violations
python architecture_guard.py --check-domain

# Run linting
make lint

# Run type checking
make type
```

## Rollback

If something goes wrong:

```bash
# Discard uncommitted changes
git checkout -- .

# Or revert the commit
git revert HEAD

# Or reset to previous state (dangerous!)
git reset --hard HEAD~1
```

## Progress Tracking

Use this checklist to track progress:

### Phase 1: Domain Layer
- [ ] Run dry-run and review output
- [ ] Execute script
- [ ] Manually move files per checklist
- [ ] Update imports
- [ ] Run tests
- [ ] Commit changes

### Phase 2: Application Layer
- [ ] Run script (when available)
- [ ] Update imports
- [ ] Run tests
- [ ] Commit changes

### Phase 3: Infrastructure
- [ ] Run script (when available)
- [ ] Update imports
- [ ] Run tests
- [ ] Commit changes

### Phase 4: Interfaces
- [ ] Run script (when available)
- [ ] Update imports
- [ ] Run tests
- [ ] Commit changes

### Phase 5: Final Validation
- [ ] All tests passing
- [ ] No import errors
- [ ] Architecture validation passes
- [ ] Documentation updated

## Support

If you encounter issues:
1. Check the dry-run output carefully
2. Review the detailed plan in `docs/ARCHITECTURE_RESTRUCTURE_PLAN.md`
3. Consult the visual guide in `docs/ARCHITECTURE_RESTRUCTURE_DIAGRAM.md`
4. Create an issue with error messages and context

## Contributing

When creating new restructuring scripts:
1. Follow the same safety pattern (dry-run, confirmation, reporting)
2. Document all changes clearly
3. Test thoroughly before committing
4. Update this README

## References

- [✨.md](../docs/✨.md) - Architecture specification
- [ARCHITECTURE_RESTRUCTURE_PLAN.md](../docs/ARCHITECTURE_RESTRUCTURE_PLAN.md) - Detailed plan
- [ARCHITECTURE_RESTRUCTURE_DIAGRAM.md](../docs/ARCHITECTURE_RESTRUCTURE_DIAGRAM.md) - Visual guide
