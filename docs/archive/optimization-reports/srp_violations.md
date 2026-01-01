# Single Responsibility Principle (SRP) Violations

**Total Violations Found**: 1

## Summary by Severity
- **CRITICAL**: 0 modules
- **HIGH**: 0 modules
- **MEDIUM**: 0 modules
- **LOW**: 1 modules

## LOW Severity Violations

### app/infrastructure/utils/keys.py
**Responsibilities**: validation, persistence
**Functions**: 10 | **Classes**: 1 | **Size**: 1768 bytes

**Details**:
- Validation: validate_symbol
- Persistence: cache_data

**Recommendation**: Extract 1 validation functions to `keys_validation.py` | Extract 1 persistence functions to `keys_persistence.py`

## Action Items

### Immediate (CRITICAL/HIGH)

### Future Improvements (MEDIUM/LOW)
- [ ] Consider refactoring `app/infrastructure/utils/keys.py`

